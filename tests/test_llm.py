import requests

from jobflow.llm import client as llm
from jobflow.utils import config


class _Ok:
    status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        return {"choices": [{"message": {"content": "hello"}}]}


def test_chat_retries_after_a_timeout(monkeypatch):
    calls = []

    def post(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise requests.exceptions.Timeout("slow")
        return _Ok()

    monkeypatch.setenv("LLM_API_KEY", "test")
    monkeypatch.setattr(llm.requests, "post", post)
    monkeypatch.setattr("time.sleep", lambda s: None)

    assert llm.OpenAICompatClient("m", "https://example.com", 0).chat("sys", "user") == "hello"
    assert len(calls) == 2


def test_empty_env_var_uses_the_default(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "")
    assert config._sub_env("${LLM_BASE_URL:https://api.groq.com/openai/v1}") == "https://api.groq.com/openai/v1"
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:11434/v1")
    assert config._sub_env("${LLM_BASE_URL:https://api.groq.com/openai/v1}") == "http://localhost:11434/v1"
