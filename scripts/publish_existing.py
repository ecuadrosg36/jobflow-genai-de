
import sqlite3
import pandas as pd
from pathlib import Path
from jobflow.utils.config import load_config
from jobflow.publish.website import publish_to_website

def main():
    config_path = "config/config.yaml"
    cfg = load_config(config_path)
    db_path = cfg["storage"]["sqlite_path"]
    
    print(f"Reading jobs from {db_path}...")
    
    con = sqlite3.connect(db_path)
    query = """
    SELECT j.job_id, j.title, j.company, j.location, j.job_url, j.description_raw, s.score_global
    FROM jobs j
    JOIN scores s ON j.job_id = s.job_id
    ORDER BY s.score_global DESC
    LIMIT 20
    """
    
    df = pd.read_sql_query(query, con)
    con.close()
    
    if df.empty:
        print("No scored jobs found in DB.")
        return

    print(f"Found {len(df)} scored jobs.")
    publish_to_website(df)

if __name__ == "__main__":
    main()
