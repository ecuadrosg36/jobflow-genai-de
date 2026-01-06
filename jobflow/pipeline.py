import datetime as dt
from pathlib import Path
import pandas as pd

from jobflow.utils.config import load_config
from jobflow.utils.cv import load_cv_text
from jobflow.ingest.jobspy_ingest import ingest
from jobflow.transform.normalize import normalize
from jobflow.storage.db import init_db, upsert_jobs, fetch_jobs_to_score, upsert_scores, mark_generated
from jobflow.rank.score import score_jobs
from jobflow.generate.pack import generate
from jobflow.publish.website import publish_to_website


def run_once(config_path: str):
    cfg = load_config(config_path)
    init_db(cfg["storage"]["sqlite_path"])

    cv_text = load_cv_text("data/cv.pdf")

    df = ingest(cfg)
    if df is None or df.empty:
        print("No jobs ingested.")
        return

    rows = normalize(df)
    upsert_jobs(cfg["storage"]["sqlite_path"], rows)

    jobs = fetch_jobs_to_score(cfg["storage"]["sqlite_path"])
    if not jobs:
        print("No jobs to score.")
        return

    # Join description into scored rows for generation
    scored = score_jobs(jobs, cv_text, cfg)
    if not scored:
        print("No jobs passed the threshold.")
        return

    upsert_scores(cfg["storage"]["sqlite_path"], scored)

    today = dt.date.today().isoformat()
    outdir = Path(cfg["output"]["base_dir"]) / today
    outdir.mkdir(parents=True, exist_ok=True)

    top = sorted(scored, key=lambda x: x["score_global"], reverse=True)[: int(cfg.get("daily_top_n", 15))]

    # Save top list
    pd.DataFrame(top).to_csv(outdir / "top_jobs.csv", index=False, encoding="utf-8")

    if cfg["llm"].get("enabled", True):
        generate(top, cv_text, cfg, outdir)

    mark_generated(cfg["storage"]["sqlite_path"], [r["job_id"] for r in top])
    
    # Publish to Website
    top_df = pd.DataFrame(top)
    publish_to_website(top_df)

    print(f"Done. Output: {outdir}")
