import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
  job_id TEXT PRIMARY KEY,
  source TEXT,
  title TEXT,
  company TEXT,
  location TEXT,
  job_url TEXT,
  description_raw TEXT,
  language TEXT,
  dedupe_key TEXT,
  inserted_at TEXT DEFAULT (datetime('now')),
  generated INTEGER DEFAULT 0
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_dedupe ON jobs(dedupe_key);

CREATE TABLE IF NOT EXISTS scores (
  job_id TEXT PRIMARY KEY,
  score_global REAL,
  score_overlap REAL,
  score_must REAL,
  score_nice REAL,
  scored_at TEXT DEFAULT (datetime('now'))
);
"""


def init_db(path: str):
    con = sqlite3.connect(path)
    try:
        con.executescript(SCHEMA)
        con.commit()
    finally:
        con.close()


def upsert_jobs(path: str, rows):
    con = sqlite3.connect(path)
    try:
        for r in rows:
            con.execute(
                """INSERT OR IGNORE INTO jobs(job_id, source, title, company, location, job_url, description_raw, language, dedupe_key)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                (str(r["job_id"]), r.get("source"), r.get("title"), r.get("company"), r.get("location"), r.get("job_url"),
                 r.get("description_raw"), r.get("language"), r.get("dedupe_key"))
            )
        con.commit()
    finally:
        con.close()


def fetch_jobs_to_score(path: str):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    try:
        cur = con.execute("SELECT * FROM jobs WHERE generated = 0")
        return [dict(x) for x in cur.fetchall()]
    finally:
        con.close()


def upsert_scores(path: str, rows):
    con = sqlite3.connect(path)
    try:
        for r in rows:
            con.execute(
                """INSERT INTO scores(job_id, score_global, score_overlap, score_must, score_nice)
                   VALUES(?,?,?,?,?)
                   ON CONFLICT(job_id) DO UPDATE SET
                     score_global=excluded.score_global,
                     score_overlap=excluded.score_overlap,
                     score_must=excluded.score_must,
                     score_nice=excluded.score_nice,
                     scored_at=datetime('now')""",
                (str(r["job_id"]), float(r["score_global"]), float(r["score_overlap"]), float(r["score_must"]), float(r["score_nice"]))
            )
        con.commit()
    finally:
        con.close()


def mark_generated(path: str, job_ids):
    con = sqlite3.connect(path)
    try:
        con.executemany("UPDATE jobs SET generated = 1 WHERE job_id = ?", [(str(j),) for j in job_ids])
        con.commit()
    finally:
        con.close()
