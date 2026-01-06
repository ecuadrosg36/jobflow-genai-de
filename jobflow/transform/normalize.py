import re


def clean(s):
    if not isinstance(s, str):
        return ""
    return re.sub(r"\s+", " ", s).strip()


def guess_lang(text: str) -> str:
    t = (text or "").lower()
    if any(w in t for w in ["responsabilidades", "requisitos", "postula", "experiencia"]):
        return "es"
    if any(w in t for w in ["responsibilities", "requirements", "apply", "experience"]):
        return "en"
    return "und"


def normalize(df):
    rows = []
    for idx, r in df.iterrows():
        job_id = str(r.get("id", idx))
        title = clean(r.get("title", ""))
        company = clean(r.get("company", ""))
        location = clean(r.get("location", ""))
        job_url = r.get("job_url") or r.get("link") or ""
        desc = clean(r.get("description", ""))
        if not title or not company or not job_url:
            continue
        rows.append({
            "job_id": job_id,
            "source": r.get("site") or r.get("source") or "unknown",
            "title": title,
            "company": company,
            "location": location,
            "job_url": job_url,
            "description_raw": desc,
            "language": guess_lang(desc),
            "dedupe_key": (title.lower() + "|" + company.lower() + "|" + location.lower())[:300],
        })
    return rows
