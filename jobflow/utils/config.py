import os
import re
import yaml

_env_pattern = re.compile(r"\$\{([^:}]+):?([^}]*)\}")


def _sub_env(v):
    if isinstance(v, str):
        def repl(m):
            key, default = m.group(1), m.group(2)
            return os.getenv(key, default)
        return _env_pattern.sub(repl, v)
    if isinstance(v, dict):
        return {k: _sub_env(val) for k, val in v.items()}
    if isinstance(v, list):
        return [_sub_env(x) for x in v]
    return v


def load_config(path: str):
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return _sub_env(raw)
