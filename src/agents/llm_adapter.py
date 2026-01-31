import os
import requests


class LLMAdapter:
    """Lightweight adapter for OpenRouter-like APIs.

    Configure with environment variables:
    - OPENROUTER_API_KEY: API key
    - OPENROUTER_URL: optional base URL (defaults to a common OpenRouter path)

    The adapter makes a best-effort to extract text from common response shapes.
    """

    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url or os.getenv("OPENROUTER_URL", "https://api.openrouter.ai/v1/chat/completions")

    def available(self):
        return bool(self.api_key)

    def generate(self, prompt, max_tokens=512, model=None):
        if not self.api_key:
            return None
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
        if model:
            payload["model"] = model
        try:
            resp = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            # Try common OpenAI-like shapes
            if isinstance(data, dict):
                choices = data.get("choices")
                if choices and len(choices) > 0:
                    first = choices[0]
                    # chat completion shape
                    if isinstance(first, dict) and first.get("message"):
                        return first["message"].get("content")
                    # text completion shape
                    if first.get("text"):
                        return first.get("text")
                # fallback: top-level text
                if data.get("text"):
                    return data.get("text")
            return None
        except Exception:
            return None
