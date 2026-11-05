"""Local configuration. Never print or persist credential values."""

import os
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def settings():
    values = {}
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, raw = line.removeprefix("export ").split("=", 1)
            if key.strip() in {"LLM_PROVIDER", "OLLAMA_MODEL", "OLLAMA_BASE_URL", "OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_BASE_URL", "LLM_TIMEOUT", "LLM_MAX_ATTEMPTS", "LLM_TEMPERATURE"}:
                tokens = shlex.split(raw, comments=True)
                values[key.strip()] = " ".join(tokens)
    values.update(os.environ)
    return values


@dataclass
class Config:
    api_key: str = field(default="", repr=False)
    model: str = "gpt-4.1-mini"
    base_url: str = "https://api.openai.com/v1"
    timeout: float = 45.0
    max_attempts: int = 2
    temperature: float = 0.7
    provider: str = "openai"

    @classmethod
    def load(cls):
        env = settings()
        provider = env.get("LLM_PROVIDER", "openai").lower()
        if provider not in {"openai", "ollama"}:
            raise ValueError("LLM_PROVIDER must be openai or ollama.")
        local = provider == "ollama"
        config = cls(api_key="" if local else env.get("OPENAI_API_KEY", ""), model=env.get("OLLAMA_MODEL", "qwen3:4b") if local else env.get("OPENAI_MODEL", "gpt-4.1-mini"), base_url=(env.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434") if local else env.get("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/"), timeout=float(env.get("LLM_TIMEOUT", 180 if local else 45)), max_attempts=int(env.get("LLM_MAX_ATTEMPTS", 2)), temperature=float(env.get("LLM_TEMPERATURE", .7)), provider=provider)
        parsed = urlsplit(config.base_url)
        if local:
            if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"} or parsed.path not in {"", "/"} or config.model.endswith(":cloud"):
                raise ValueError("Ollama mode requires a loopback HTTP endpoint and a local model.")
        elif parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("OPENAI_BASE_URL must be HTTPS.")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("Endpoint must not contain credentials/query/fragment.")
        if not config.model.strip() or not 1 <= config.max_attempts <= 3 or not 1 <= config.timeout <= 600 or not 0 <= config.temperature <= 2:
            raise ValueError("Invalid model, timeout, temperature, or attempt configuration.")
        return config

    def public(self):
        result = {"provider": self.provider, "model": self.model, "base_url": self.base_url, "timeout": self.timeout, "max_attempts": self.max_attempts, "temperature": self.temperature}
        if self.provider == "ollama":
            result.update(num_ctx=16384, num_predict=1800, think=False)
        return result
