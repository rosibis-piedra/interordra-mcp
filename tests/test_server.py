import asyncio
import json
from types import SimpleNamespace

import pytest

import server


def get_annotations(tool_name):
    return asyncio.run(server.mcp.get_tool(tool_name)).annotations


# ── ToolAnnotations hints ──────────────────────────────────────────────

@pytest.mark.parametrize("tool_name", ["detectar_gap", "reformular_pregunta", "analizar_conversacion"])
def test_tool_declares_all_four_hints(tool_name):
    annotations = get_annotations(tool_name)
    assert annotations.readOnlyHint is not None
    assert annotations.destructiveHint is not None
    assert annotations.idempotentHint is not None
    assert annotations.openWorldHint is not None


def test_tools_are_read_only_and_non_destructive():
    for tool_name in ("detectar_gap", "reformular_pregunta", "analizar_conversacion"):
        annotations = get_annotations(tool_name)
        assert annotations.readOnlyHint is True
        assert annotations.destructiveHint is False


def test_tools_that_call_external_apis_declare_open_world():
    # All three tools reach out to Voyage AI and/or the Anthropic API.
    for tool_name in ("detectar_gap", "reformular_pregunta", "analizar_conversacion"):
        assert get_annotations(tool_name).openWorldHint is True


# ── detectar_gap ────────────────────────────────────────────────────────

def test_detectar_gap_identical_texts_have_no_gap():
    result = server.detectar_gap("hola mundo", "hola mundo")
    assert result["gap_score"] == 0.0
    assert result["nivel"] == "bajo"
    assert result["metodo"] == "lexical_fallback"


def test_detectar_gap_unrelated_texts_have_high_gap():
    result = server.detectar_gap(
        "el gato duerme en el sofa",
        "la bolsa de valores subio hoy en wall street",
    )
    assert result["gap_score"] > 0.6
    assert result["nivel"] == "alto"
    assert "palabras_solo_en_A" in result
    assert "palabras_solo_en_B" in result


def test_detectar_gap_falls_back_to_lexical_when_api_unavailable():
    # no_real_network fixture blocks urlopen, so no real Voyage/Anthropic
    # call can succeed here.
    result = server.detectar_gap("comida saludable", "recetas de cocina saludable")
    assert result["metodo"] == "lexical_fallback"


def test_detectar_gap_returns_structured_error_on_unexpected_failure(monkeypatch):
    def _boom(*args, **kwargs):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(server, "semantic_similarity", _boom)
    result = server.detectar_gap("a", "b")
    assert result["error"] is True
    assert "simulated failure" in result["mensaje"]


# ── analizar_conversacion ───────────────────────────────────────────────

def test_analizar_conversacion_detects_gaps_between_messages():
    result = server.analizar_conversacion([
        "hola, como estas hoy",
        "hola, como estas",
        "el clima esta soleado y agradable hoy",
    ])
    assert len(result["gaps_detectados"]) == 2
    assert "gap_promedio" in result
    assert "punto_critico" in result
    assert "diagnostico" in result


def test_analizar_conversacion_requires_at_least_two_messages():
    result = server.analizar_conversacion(["solo un mensaje"])
    assert result == {
        "error": True,
        "mensaje": "Se necesitan al menos 2 mensajes para analizar una conversación.",
    }


def test_analizar_conversacion_returns_structured_error_on_unexpected_failure(monkeypatch):
    def _boom(*args, **kwargs):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(server, "semantic_similarity", _boom)
    result = server.analizar_conversacion(["mensaje uno", "mensaje dos"])
    assert result["error"] is True
    assert "simulated failure" in result["mensaje"]


# ── reformular_pregunta ─────────────────────────────────────────────────

def test_reformular_pregunta_uses_template_fallback_without_api_key():
    # no_real_network fixture already removed ANTHROPIC_API_KEY, so
    # get_client() raises and the template fallback kicks in.
    result = server.reformular_pregunta("Como optimizo mi codigo?")
    assert result["pregunta_original"] == "Como optimizo mi codigo?"
    assert len(result["variantes"]) == 3
    assert "instruccion" in result


def test_reformular_pregunta_uses_llm_when_client_available(monkeypatch):
    fake_response = SimpleNamespace(
        content=[SimpleNamespace(text=json.dumps({
            "variantes": ["variante 1", "variante 2", "variante 3"],
        }))]
    )
    fake_client = SimpleNamespace(
        messages=SimpleNamespace(create=lambda **kwargs: fake_response)
    )
    monkeypatch.setattr(server, "get_client", lambda: fake_client)

    result = server.reformular_pregunta("Por que mi API falla?")
    assert result["variantes"] == ["variante 1", "variante 2", "variante 3"]


def test_reformular_pregunta_returns_structured_error_on_unexpected_failure():
    # With no ANTHROPIC_API_KEY, get_client() raises inside the inner
    # try/except, so the template fallback runs. Passing a non-string then
    # breaks the fallback itself (pregunta.lower()), which should be caught
    # by the outer try/except and reported as a structured error instead of
    # propagating.
    result = server.reformular_pregunta(None)
    assert result["error"] is True
    assert "mensaje" in result
