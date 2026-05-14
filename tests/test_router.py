"""Tests del router: scoring, routing local, fallback cloud."""

import pytest
from unittest.mock import patch, MagicMock

from jarvis.router import (
    _score_prompt,
    _is_bad_response,
    _approx_tokens,
    _estimate_cost,
    route,
    RouteResult,
)


class TestScoring:
    def test_simple_prompt_stays_local(self):
        score, _ = _score_prompt("Hola, ¿cómo estás?")
        assert score == 0

    def test_code_keyword_triggers_cloud(self):
        score, reason = _score_prompt("escribe una función en python para ordenar una lista")
        assert score > 0
        assert "python" in reason or "función" in reason

    def test_long_prompt_adds_score(self):
        long_prompt = "x " * 260
        score, reason = _score_prompt(long_prompt)
        assert score >= 2
        assert "prompt largo" in reason

    def test_multiple_triggers_accumulate(self):
        score1, _ = _score_prompt("¿por qué python es mejor?")
        score2, _ = _score_prompt("hola mundo")
        assert score1 > score2

    def test_arquitectura_triggers_cloud(self):
        score, _ = _score_prompt("diseña la arquitectura de un sistema distribuido")
        assert score > 0


class TestBadResponse:
    def test_empty_is_bad(self):
        assert _is_bad_response("") is True

    def test_short_is_bad(self):
        assert _is_bad_response("ok") is True

    def test_i_dont_know_is_bad(self):
        assert _is_bad_response("I don't know the answer to that.") is True

    def test_no_puedo_is_bad(self):
        assert _is_bad_response("No puedo responder esa pregunta.") is True

    def test_valid_response_is_good(self):
        assert _is_bad_response("Python es un lenguaje de programación interpretado.") is False


class TestCostEstimation:
    def test_local_cost_is_zero(self):
        assert _estimate_cost(1000, "local") == 0.0

    def test_cloud_cost_positive(self):
        cost = _estimate_cost(1000, "cloud")
        assert cost > 0
        assert cost == round(1000 * 0.00002, 6)

    def test_approx_tokens(self):
        assert _approx_tokens("hola") >= 1
        assert _approx_tokens("a" * 400) == 100


class TestRouteLocal:
    def test_simple_prompt_uses_local(self):
        with patch("jarvis.router.ask_local", return_value="Soy un asistente local muy útil.") as mock_local, \
             patch("jarvis.router.ask_cloud") as mock_cloud, \
             patch("jarvis.router.record_usage"):
            result = route("Hola, ¿cómo estás?")

        assert result.source == "local"
        mock_local.assert_called_once()
        mock_cloud.assert_not_called()

    def test_local_result_has_zero_cost(self):
        with patch("jarvis.router.ask_local", return_value="Respuesta local correcta y completa."), \
             patch("jarvis.router.record_usage"):
            result = route("¿Qué hora es?")

        assert result.estimated_cost == 0.0
        assert result.source == "local"


class TestRouteFallback:
    def test_local_failure_falls_back_to_cloud(self):
        with patch("jarvis.router.ask_local", side_effect=RuntimeError("Ollama no disponible")), \
             patch("jarvis.router.ask_cloud", return_value="Respuesta desde la nube.") as mock_cloud, \
             patch("jarvis.router.record_usage"):
            result = route("¿Qué hora es?")

        assert result.source == "cloud"
        mock_cloud.assert_called_once()
        assert "fallback" in result.reason

    def test_bad_local_response_triggers_fallback(self):
        with patch("jarvis.router.ask_local", return_value="No sé"), \
             patch("jarvis.router.ask_cloud", return_value="Respuesta cloud completa y útil."), \
             patch("jarvis.router.record_usage"):
            result = route("¿Qué hora es?")

        assert result.source == "cloud"

    def test_cloud_prompt_skips_local(self):
        with patch("jarvis.router.ask_local") as mock_local, \
             patch("jarvis.router.ask_cloud", return_value="Arquitectura bien diseñada."), \
             patch("jarvis.router.record_usage"):
            result = route("diseña la arquitectura de un sistema de microservicios con python")

        assert result.source == "cloud"
        mock_local.assert_not_called()
