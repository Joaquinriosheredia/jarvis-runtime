import logging

import requests

from jarvis.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)


def ask_local(prompt: str, model: str = OLLAMA_MODEL) -> str:
    try:
        res = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=OLLAMA_TIMEOUT,
        )
        res.raise_for_status()
        data = res.json()
        if "response" not in data:
            raise ValueError(f"Unexpected Ollama response: {data}")
        return data["response"]
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Ollama no disponible en localhost:11434")
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Ollama timeout después de {OLLAMA_TIMEOUT}s")
    except Exception as e:
        raise RuntimeError(f"Local LLM error: {e}")
