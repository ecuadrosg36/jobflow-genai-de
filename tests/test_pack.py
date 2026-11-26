from pathlib import Path

from jobflow.generate import pack


def test_render_pdf_passes_paths_as_arguments_not_shell(monkeypatch):
    calls = []
    monkeypatch.setattr(pack.subprocess, "run", lambda args, **kw: calls.append((args, kw)))

    job_dir = Path("output/job_1; touch pwned_pack")  # job_id comes from scraped postings
    pack.render_pdf(job_dir / "cv_tailored.yaml", job_dir)

    args, kw = calls[0]
    assert args == ["rendercv", "render", str(job_dir / "cv_tailored.yaml"), "--output-folder", str(job_dir)]
    assert kw == {"check": True}  # no shell=True


def test_cv_yaml_path_prefers_local_copy(tmp_path):
    (tmp_path / "cv.yaml").write_text("cv: {}", encoding="utf-8")
    assert pack.cv_yaml_path(tmp_path) == tmp_path / "cv.yaml"

    (tmp_path / "cv.local.yaml").write_text("cv: {}", encoding="utf-8")
    assert pack.cv_yaml_path(tmp_path) == tmp_path / "cv.local.yaml"
