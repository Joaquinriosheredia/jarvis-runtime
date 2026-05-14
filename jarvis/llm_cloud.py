import logging

from openai import OpenAI, AuthenticationError, RateLimitError, APIError

from jarvis.config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY no configurada en .env")
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def ask_cloud(prompt: str, model: str = OPENAI_MODEL) -> str:
    try:
        client = _get_client()
        res = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        content = res.choices[0].message.content
        if not content:
            raise ValueError("OpenAI devolvió respuesta vacía")
        return content
    except AuthenticationError:
        raise RuntimeError("OPENAI_API_KEY inválida o expirada")
    except RateLimitError:
        raise RuntimeError("OpenAI rate limit alcanzado")
    except APIError as e:
        raise RuntimeError(f"OpenAI API error: {e}")
