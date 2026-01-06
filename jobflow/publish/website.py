
import json
import shutil
from pathlib import Path
import pandas as pd

def publish_to_website(top_jobs: pd.DataFrame, website_path: str = "../enmacuadroswork/public/data"):
    """
    Exports the top jobs to a JSON file in the website's public directory.
    This allows the portfolio website to display a 'Live Job Board'.
    """
    web_dir = Path(website_path)
    web_dir = Path(website_path)
    if not web_dir.exists():
        print(f"⚠️ Website directory {web_dir} not found. Creating it...")
        web_dir.mkdir(parents=True, exist_ok=True)

    # Convert to list of dicts
    jobs_list = top_jobs.to_dict(orient="records")
    
    # Add timestamp
    output_data = {
        "updated_at": pd.Timestamp.now().isoformat(),
        "jobs": jobs_list
    }

    target_file = web_dir / "latest_jobs.json"
    
    print(f"🚀 Publishing {len(jobs_list)} jobs to {target_file}...")
    try:
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print("✅ Published successfully!")
    except Exception as e:
        print(f"❌ Failed to publish to website: {e}")
