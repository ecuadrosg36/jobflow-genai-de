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


def test_parse_summary_accepts_only_a_short_list_of_strings():
    assert pack.parse_summary('```json\n{"summary": [" Built pipelines. "]}\n```') == ["Built pipelines."]
    assert pack.parse_summary("not json") is None
    assert pack.parse_summary('{"summary": "one string, not a list"}') is None
    assert pack.parse_summary('{"summary": []}') is None
    assert pack.parse_summary('{"summary": ["' + "x" * 401 + '"]}') is None
    assert pack.parse_summary('{"summary": [{"cv": {"email": "x"}}]}') is None


class _FakeClient:
    def __init__(self, **kwargs):
        self.prompts = []

    def chat(self, system, user):
        self.prompts.append(user)
        if "CV_YAML" in user:
            return '{"summary": ["Tailored for this job."]}'
        return "text long enough to be cached by the pack generator, more than fifty bytes."


def test_each_job_starts_from_the_base_cv(tmp_path, monkeypatch):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "cv.yaml").write_text("cv:\n  sections:\n    summary: [Base summary.]\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    client = _FakeClient()
    monkeypatch.setattr(pack, "OpenAICompatClient", lambda **kw: client)
    monkeypatch.setattr(pack, "render_pdf", lambda *a: None)
    monkeypatch.setattr("time.sleep", lambda s: None)

    rows = [{"job_id": i, "score_global": 1, "score_overlap": 1, "score_must": 1, "score_nice": 1} for i in ("a", "b")]
    pack.generate(rows, "cv text", {"llm": {"model": "m", "base_url": "u", "temperature": 0}}, tmp_path / "out")

    cv_prompts = [p for p in client.prompts if "CV_YAML" in p]
    assert len(cv_prompts) == 2
    assert all("Base summary." in p and "Tailored for this job." not in p for p in cv_prompts)
    assert "Tailored for this job." in (tmp_path / "out" / "job_b_pack" / "cv_tailored.yaml").read_text()
