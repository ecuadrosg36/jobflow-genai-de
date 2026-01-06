from pathlib import Path
from pypdf import PdfReader


def load_cv_text(pdf_path: str) -> str:
    p = Path(pdf_path)
    if not p.exists():
        raise FileNotFoundError(f"CV PDF not found at {pdf_path}. Place it there (see README).")
    reader = PdfReader(str(p))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()
