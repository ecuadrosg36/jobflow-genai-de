import pandas as pd
from jobspy import scrape_jobs


def ingest(cfg) -> pd.DataFrame:
    keywords = " OR ".join(cfg["search"]["keywords"])
    sites = cfg["search"]["sites"]
    location = cfg["search"]["location"]
    remote = bool(cfg["search"].get("remote", True))

    df = scrape_jobs(
        site_name=sites,
        search_term=keywords,
        location=location,
        results_wanted=60,
        hours_old=72,
        remote=remote,
    )
    return df if df is not None else pd.DataFrame()
