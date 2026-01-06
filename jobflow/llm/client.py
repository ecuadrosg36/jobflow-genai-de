import os
import requests


class OpenAICompatClient:
    def __init__(self, model: str, base_url: str, temperature: float):
        # Allow generic name (LLM_API_KEY) or standard OpenAI name
        self.api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        # Auto-set dummy key for local Ollama if missing
        if not self.api_key and "localhost" in base_url:
            self.api_key = "ollama"

        if not self.api_key:
            raise RuntimeError(
                "❌ API Key is missing!\n"
                "Please set the 'LLM_API_KEY' (or 'OPENAI_API_KEY') environment variable.\n"
                "  - If using Groq: Set it to your Groq API Key.\n"
                "  - If using Gemini: Set it to your Google API Key.\n"
                "  - If using OpenAI: Set it to your OpenAI API Key."
            )
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = float(temperature)

    def chat(self, system: str, user: str) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        import time
        import random

        max_retries = 5
        base_delay = 5  # Start from 5s
        
        for attempt in range(max_retries):
            try:
                r = requests.post(url, json=payload, headers=headers, timeout=90)
                r.raise_for_status()
                
                # Defensive: Handle empty/bad JSON
                try:
                    data = r.json()
                    if "choices" not in data or not data["choices"]:
                        print(f"⚠️ Empty LLM response attempt {attempt+1}")
                        raise ValueError("Empty LLM response")
                    return data["choices"][0]["message"]["content"]
                except ValueError as e:
                    # If JSON fails, treat as a retryable error
                    raise requests.exceptions.HTTPError(f"Bad JSON: {e}")

            except requests.exceptions.HTTPError as e:
                status = 0
                if hasattr(r, 'status_code'):
                    status = r.status_code
                
                # If Rate Limit (429) or Server Error (5xx), wait and retry
                if status == 429 or status >= 500:
                    # Exponential Backoff + Jitter
                    # 5s * 2^attempt -> 5, 10, 20, 40, 80...
                    delay = min(base_delay * (2 ** attempt), 120) 
                    # Add jitter (0.5 to 3s)
                    sleep_time = delay + random.uniform(0.5, 3.0)

                    print(f"⚠️ API Error {status}. Cooling down for {sleep_time:.2f}s before retry ({attempt+1}/{max_retries})...")
                    time.sleep(sleep_time)
                else:
                    print(f"❌ API Error: {r.text}")
                    raise e
        
        raise RuntimeError(f"Max retries ({max_retries}) exceeded.")
