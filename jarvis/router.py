import time
import logging
from dataclasses import dataclass
from typing import Literal

from jarvis.llm_local import ask_local
from jarvis.llm_cloud import ask_cloud
from jarvis.cost import record_usage

logger = logging.getLogger(__name__)

ModelSource = Literal["local", "cloud"]

BAD_PATTERNS = [
    "i don't know", "i cannot", "i'm unable",
    "no sé", "no puedo", "error", "failed",
]

CLOUD_TRIGGERS: dict[str, list[str]] = {
    "complejidad": ["arquitectura", "refactor", "diseña", "optimiza", "explica en detalle"],
    "codigo":      ["python", "java", "javascript", "typescript", "sql", "bash", "bug", "código", "función"],
    "razonamiento": ["por qué", "compara", "diferencia", "ventajas", "desventajas", "analiza"],
}


@dataclass
class RouteResult:
    response: str
    source: ModelSource
    latency: float
    reason: str
    estimated_cost: float
    tokens_approx: int


def _score_prompt(prompt: str) -> tuple[int, str]:
    """Devuelve (score, reason). Score > 0 → cloud."""
    score = 0
    reasons: list[str] = []

    if len(prompt) > 500:
        score += 2
        reasons.append("prompt largo")

    lower = prompt.lower()
    for category, keywords in CLOUD_TRIGGERS.items():
        matches = [k for k in keywords if k in lower]
        if matches:
            score += len(matches)
            reasons.append(f"{category}: {', '.join(matches)}")

    return score, " | ".join(reasons) if reasons else "ninguno"


def _is_bad_response(text: str) -> bool:
    if not text or len(text.strip()) < 10:
        return True
    lower = text.lower()
    return any(p in lower for p in BAD_PATTERNS)


def _estimate_cost(tokens: int, source: ModelSource) -> float:
    # gpt-4o-mini: ~$0.00002/token (input+output combinado)
    return round(tokens * 0.00002, 6) if source == "cloud" else 0.0


def _approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def route(prompt: str) -> RouteResult:
    score, reason = _score_prompt(prompt)
    tokens = _approx_tokens(prompt)

    if score > 0:
        start = time.time()
        response = ask_cloud(prompt)
        latency = round(time.time() - start, 2)
        total_tokens = tokens + _approx_tokens(response)
        cost = _estimate_cost(total_tokens, "cloud")
        record_usage("cloud", total_tokens, cost)
        return RouteResult(
            response=response,
            source="cloud",
            latency=latency,
            reason=f"cloud forzado ({reason})",
            estimated_cost=cost,
            tokens_approx=total_tokens,
        )

    # intenta local primero
    try:
        start = time.time()
        response = ask_local(prompt)
        latency = round(time.time() - start, 2)

        if _is_bad_response(response):
            raise ValueError("respuesta local inválida")

        total_tokens = tokens + _approx_tokens(response)
        record_usage("local", total_tokens, 0.0)
        return RouteResult(
            response=response,
            source="local",
            latency=latency,
            reason="local suficiente",
            estimated_cost=0.0,
            tokens_approx=total_tokens,
        )

    except Exception as e:
        logger.warning(f"Local falló ({e}), usando cloud")
        start = time.time()
        response = ask_cloud(prompt)
        latency = round(time.time() - start, 2)
        total_tokens = tokens + _approx_tokens(response)
        cost = _estimate_cost(total_tokens, "cloud")
        record_usage("cloud", total_tokens, cost)
        return RouteResult(
            response=response,
            source="cloud",
            latency=latency,
            reason=f"fallback por error local: {e}",
            estimated_cost=cost,
            tokens_approx=total_tokens,
        )
