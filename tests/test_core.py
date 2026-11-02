import pandas as pd

from jobflow.rank.score import score_jobs
from jobflow.storage.db import fetch_jobs_to_score, init_db, mark_generated, upsert_jobs
from jobflow.transform.normalize import normalize


def _postings():
    return pd.DataFrame(
        [
            {
                "id": "1",
                "site": "linkedin",
                "title": "  Senior   Data Engineer ",
                "company": "Acme",
                "location": "Remote",
                "job_url": "https://example.com/1",
                "description": "Requirements: Python, dbt, Airflow and Snowflake experience.",
            },
            {
                "id": "2",
                "site": "indeed",
                "title": "Data Engineer",
                "company": "",
                "location": "Lima",
                "job_url": "https://example.com/2",
                "description": "Missing company, should be dropped.",
            },
        ]
    )


def test_normalize_cleans_text_and_drops_incomplete_rows():
    rows = normalize(_postings())
    assert len(rows) == 1
    row = rows[0]
    assert row["title"] == "Senior Data Engineer"
    assert row["language"] == "en"
    assert row["dedupe_key"] == "senior data engineer|acme|remote"


def test_same_job_from_two_boards_is_stored_once(tmp_path):
    db = str(tmp_path / "jobs.db")
    init_db(db)
    row = normalize(_postings())[0]
    duplicate = {**row, "job_id": "99", "source": "glassdoor"}
    upsert_jobs(db, [row, duplicate])
    assert len(fetch_jobs_to_score(db)) == 1


def test_generated_jobs_are_not_scored_again(tmp_path):
    db = str(tmp_path / "jobs.db")
    init_db(db)
    upsert_jobs(db, normalize(_postings()))
    mark_generated(db, ["1"])
    assert fetch_jobs_to_score(db) == []


def test_score_ranks_matching_job_and_filters_weak_ones():
    cfg = {
        "filters": {
            "must_have_any": ["python", "sql"],
            "nice_to_have_any": ["dbt", "airflow"],
            "min_match_score": 0.2,
        }
    }
    jobs = [
        {"job_id": "good", "title": "Data Engineer", "description_raw": "Python SQL dbt Airflow pipelines"},
        {"job_id": "bad", "title": "Sales Manager", "description_raw": "Manage retail sales team"},
    ]
    cv = "Data engineer with Python, SQL, dbt and Airflow pipelines"
    scored = score_jobs(jobs, cv, cfg)
    assert [s["job_id"] for s in scored] == ["good"]
    assert 0 < scored[0]["score_global"] <= 1
