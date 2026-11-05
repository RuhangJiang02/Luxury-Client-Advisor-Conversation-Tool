"""OpenAI HTTP adapter. No automatic library retries or error-body logging."""

import requests


class ProviderError(Exception):
    def __init__(self, code, retryable=False):
        super().__init__(code)
        self.code = code
        self.retryable = retryable


class OpenAIAdapter:
    is_live = True

    def __init__(self, config, transport=None):
        self.config = config
        self.transport = transport or requests

    @property
    def available(self):
        return bool(self.config.api_key)

    def complete(self, messages):
        if not self.available:
            raise ProviderError("CONFIG_MISSING")
        payload = {"model": self.config.model, "messages": messages, "response_format": {"type": "json_object"}, "temperature": self.config.temperature, "max_completion_tokens": 1800}
        try:
            response = self.transport.post(self.config.base_url + "/chat/completions", headers={"Authorization": "Bearer " + self.config.api_key, "Content-Type": "application/json"}, json=payload, timeout=self.config.timeout)
        except requests.RequestException:
            raise ProviderError("NETWORK_ERROR", retryable=True) from None
        if response.status_code != 200:
            if response.status_code == 429:
                # Read only allowlisted machine codes, never log raw provider bodies.
                try:
                    error = response.json().get("error", {})
                    code = error.get("code")
                    terminal = {"insufficient_quota", "credit_balance_exhausted", "organization_spend_limit_exceeded", "project_spend_limit_exceeded", "organization_usage_limit_exceeded", "billing_hard_limit_reached"}
                    if code in terminal:
                        raise ProviderError("QUOTA_" + code.upper())
                except (ValueError, AttributeError, TypeError):
                    pass
            raise ProviderError(f"HTTP_{response.status_code}", retryable=response.status_code == 429 or response.status_code >= 500)
        try:
            data = response.json()
            choice = data["choices"][0]
            content = choice["message"].get("content")
            if not isinstance(content, str):
                raise ValueError("No content")
            usage = data.get("usage") or {}
            return {"content": content, "finish_reason": choice.get("finish_reason"), "provider_response_id": data.get("id"), "reported_model": data.get("model"), "usage": {k: usage.get(k) for k in ["prompt_tokens", "completion_tokens", "total_tokens"]}}
        except (ValueError, KeyError, IndexError, TypeError):
            raise ProviderError("PROVIDER_PAYLOAD_INVALID", retryable=True) from None


class OllamaAdapter:
    """Genuine local inference via Ollama; never sends an OpenAI credential."""

    is_live = True
    available = True

    def __init__(self, config, transport=None):
        self.config = config
        if transport is None:
            self.transport = requests.Session()
            self.transport.trust_env = False  # Loopback calls must not use an external proxy.
        else:
            self.transport = transport

    def complete(self, messages):
        payload = {"model": self.config.model, "messages": messages, "stream": False, "format": "json", "think": False, "options": {"temperature": self.config.temperature, "num_predict": 1800, "num_ctx": 16384}, "keep_alive": "10m"}
        try:
            response = self.transport.post(self.config.base_url + "/api/chat", json=payload, timeout=self.config.timeout)
        except requests.RequestException:
            raise ProviderError("OLLAMA_UNREACHABLE", retryable=False) from None
        if response.status_code != 200:
            raise ProviderError("OLLAMA_MODEL_MISSING" if response.status_code == 404 else f"OLLAMA_HTTP_{response.status_code}", retryable=response.status_code >= 500)
        try:
            data = response.json()
            content = data["message"]["content"]
            if not isinstance(content, str) or data.get("done") is not True:
                raise ValueError("Incomplete local output")
            prompt_tokens, completion_tokens = data.get("prompt_eval_count", 0), data.get("eval_count", 0)
            return {"content": content, "finish_reason": data.get("done_reason", "stop"), "reported_model": data.get("model"), "provider_response_id": None, "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens, "total_tokens": prompt_tokens + completion_tokens}}
        except (ValueError, KeyError, TypeError):
            raise ProviderError("PROVIDER_PAYLOAD_INVALID", retryable=True) from None
