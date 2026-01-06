import csv
import json
import yaml
import os
import shutil
from pathlib import Path
from jobflow.llm.client import OpenAICompatClient
from jobflow.llm.prompts import system_for, resume_user, cover_user, msg_user, update_cv_user

def generate(top_rows, cv_text: str, cfg, outdir: Path):
    llm_cfg = cfg["llm"]
    client = OpenAICompatClient(
        model=llm_cfg["model"],
        base_url=llm_cfg["base_url"],
        temperature=llm_cfg["temperature"],
    )

    # 1. Load Base CV YAML
    cv_yaml_path = Path("data/cv.yaml")
    base_cv = {}
    if cv_yaml_path.exists():
        base_cv = yaml.safe_load(cv_yaml_path.read_text(encoding="utf-8"))

    for r in top_rows:
        lang = "en" if (r.get("language") == "en") else "es"
        job = {
            "job_id": r["job_id"],
            "title": r.get("title"),
            "company": r.get("company"),
            "location": r.get("location"),
            "job_url": r.get("job_url"),
            "description_raw": r.get("description_raw", ""),
        }

        job_dir = outdir / f"job_{job['job_id']}_pack"
        job_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata
        (job_dir / "job.json").write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
        (job_dir / "score.json").write_text(json.dumps({k: r[k] for k in ["score_global","score_overlap","score_must","score_nice"]}, ensure_ascii=False, indent=2), encoding="utf-8")

        sys = system_for(lang)
        
        # 2. Generate Cover Letter & Message (Use YAML if available for better quality/tokens)
        cv_source = yaml.dump(base_cv) if base_cv else cv_text
        
        cover_path = job_dir / f"cover_letter_{lang.upper()}.txt"
        msg_path = job_dir / "linkedin_message.txt"

        # Caching: Skip if already generated (size > 50 bytes)
        if cover_path.exists() and cover_path.stat().st_size > 50:
            print(f"Skipping cached Cover Letter for Job {job['job_id']}")
        else:
            (job_dir / f"cover_letter_{lang.upper()}.txt").write_text(client.chat(sys, cover_user(cv_source, job)), encoding="utf-8")
        
        if msg_path.exists() and msg_path.stat().st_size > 50:
            print(f"Skipping cached LinkedIn Message for Job {job['job_id']}")
        else:
            (job_dir / "linkedin_message.txt").write_text(client.chat(sys, msg_user(job, lang)), encoding="utf-8")

        # 3. Dynamic Resume with RenderCV
        if base_cv:
            try:
                # LLM Update
                updates_json = client.chat(sys, update_cv_user(yaml.dump(base_cv), job))
                updates = json.loads(updates_json.replace("```json", "").replace("```", "").strip())
                
                # Create tailored YAML
                tailored_cv = base_cv.copy()
                if "summary" in updates and "cv" in tailored_cv:
                   if "sections" in tailored_cv["cv"]:
                       tailored_cv["cv"]["sections"]["summary"] = updates["summary"]
                
                # Write tailored YAML
                tailored_yaml_path = job_dir / "cv_tailored.yaml"
                tailored_yaml_path.write_text(yaml.dump(tailored_cv, sort_keys=False), encoding="utf-8")
                
                # Run RenderCV
                # Check directly in current venv path or assume it's in path
                print(f"Generating PDF for Job {job['job_id']}...")
                os.system(f"rendercv render {tailored_yaml_path} --output-folder {job_dir}")
                
            except Exception as e:
                print(f"Error generating RenderCV PDF: {e}")
                # Fallback to Text Resume
                (job_dir / f"resume_{lang.upper()}.md").write_text(client.chat(sys, resume_user(cv_text, job)), encoding="utf-8")
        else:
             # Fallback if no cv.yaml
             (job_dir / f"resume_{lang.upper()}.md").write_text(client.chat(sys, resume_user(cv_text, job)), encoding="utf-8")
        
        # Voluntary Pacing to avoid Rate Limits
        import time
        time.sleep(5)
