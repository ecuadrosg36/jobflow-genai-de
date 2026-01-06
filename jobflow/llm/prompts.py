SYSTEM_BASE = (
    "You are an expert Data Engineering Career Coach. You write high-impact job application materials. "
    "Hard rule: DO NOT invent experience. Use ONLY facts from CV_TEXT. "
    "Focus on production reliability, scalability, and remote-work readiness (async communication, autonomy). "
    "Keep outputs professional, concise, and optimized for both ATS and human recruiters."
)


def system_for(lang: str) -> str:
    if lang == "en":
        return SYSTEM_BASE + " Write in English."
    return SYSTEM_BASE + " Write in Spanish (Peru)."


def resume_user(cv_text: str, job: dict) -> str:
    return f"""CV_TEXT:\n{cv_text}\n\nJOB_POSTING:\nTitle: {job.get('title')}\nCompany: {job.get('company')}\nLocation: {job.get('location')}\nDescription: {job.get('description_raw')}\nURL: {job.get('job_url')}\n\nTASK:\nCreate a tailored 'Project & Impact Highlights' section.\nOutput as Markdown:\n1) 5-8 high-impact bullets (only from CV_TEXT). Quantitative results preferred (e.g., % improvement, scale).\n2) Core Tech Stack line (relevant to JD).\n3) Remote Efficiency: Mention one fact from CV that shows autonomy or remote-collaboration capability.\n4) Gaps: List max 2 learning priorities based on JD.\n"""


def cover_user(cv_text: str, job: dict) -> str:
    return f"""CV_TEXT:\n{cv_text}\n\nJOB_POSTING:\nTitle: {job.get('title')}\nCompany: {job.get('company')}\nLocation: {job.get('location')}\nDescription: {job.get('description_raw')}\nURL: {job.get('job_url')}\n\nTASK:\nWrite a high-impact cover letter (180-220 words). focus on 'Why Me' for this specific role. Mention experience with production pipelines and cloud infrastructure. Highlight your ability to work independently in a remote environment. End with a strong call-to-action.\n"""


def update_cv_user(cv_yaml: str, job: dict) -> str:
    return f"""CV_YAML:\n{cv_yaml}\n\nJOB_POSTING:\nTitle: {job.get('title')}\nCompany: {job.get('company')}\nDescription: {job.get('description_raw')}\n\nTASK:\nUpdate the 'summary' section of the CV to match the Job Description keys. Focus on 'Why Me'.\nOutput ONLY valid JSON with this structure:\n{{\n  "summary": ["New tailored summary sentence 1", "New tailored summary sentence 2"]\n}}\nIMPORTANT: Escape all backslashes in your strings (e.g., use \\\\textbf instead of \\textbf). Ensure JSON is valid."""

def msg_user(job: dict, lang: str) -> str:
    return f"""TASK:\nDraft a professional LinkedIn reach-out to a recruiter for:\nTitle: {job.get('title')}\nCompany: {job.get('company')}\nURL: {job.get('job_url')}\n\nConstraints:\n- 400 characters max\n- Direct and value-oriented\n- Mention 'Senior Data Engineer' (if applicable) and expertise in production-grade pipelines.\n- Language: {'English' if lang=='en' else 'Spanish (Peru)'}\n"""
