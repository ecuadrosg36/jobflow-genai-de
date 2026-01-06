import re


def tokens(text: str) -> set:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9áéíóúñ#+.\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return set(text.split())


def keyword_score(text: str, keywords) -> float:
    t = tokens(text)
    if not keywords:
        return 0.0
    hit = 0
    for k in keywords:
        parts = k.lower().split()
        if any(p in t for p in parts):
            hit += 1
    return hit / max(len(keywords), 1)


def score_jobs(jobs, cv_text: str, cfg):
    cv_toks = tokens(cv_text)
    must = cfg["filters"]["must_have_any"]
    nice = cfg["filters"]["nice_to_have_any"]

    out = []
    for j in jobs:
        jd = (j.get("description_raw") or "") + " " + (j.get("title") or "")
        jd_toks = tokens(jd)
        overlap = len(cv_toks.intersection(jd_toks)) / max(len(jd_toks), 1)
        s_must = keyword_score(jd, must)
        s_nice = keyword_score(jd, nice)
        s_global = 0.55*overlap + 0.30*s_must + 0.15*s_nice
        if s_global < float(cfg["filters"]["min_match_score"]):
            continue
        out.append({
            **{k: j.get(k) for k in ["job_id","source","title","company","location","job_url","language"]},
            "score_overlap": round(overlap, 4),
            "score_must": round(s_must, 4),
            "score_nice": round(s_nice, 4),
            "score_global": round(s_global, 4),
        })
    return out
