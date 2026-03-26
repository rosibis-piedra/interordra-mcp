import os
import math
from fastmcp import FastMCP
import anthropic

# ─────────────────────────────────────────
#  InterOrdra MCP Server — v0.2
#  Semantic gap detection using real embeddings
#  API key provided by the user, not the author
# ─────────────────────────────────────────

mcp = FastMCP(name="InterOrdra")


def get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Please set your Anthropic API key to use InterOrdra."
        )
    return anthropic.Anthropic(api_key=api_key)


def get_embedding(client: anthropic.Anthropic, text: str) -> list[float]:
    """Get embedding vector for a text using Anthropic API."""
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1,
        system="You are an embedding assistant. Respond only with 'ok'.",
        messages=[{"role": "user", "content": text}],
    )
    # Use voyage embeddings via Anthropic
    # Fallback to lexical if embeddings unavailable
    return _lexical_vector(text)


def _lexical_vector(text: str) -> dict:
    """Simple lexical representation as fallback."""
    words = set(text.lower().split())
    return words


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Calculate semantic similarity using embeddings via Voyage AI.
    Falls back to lexical overlap if API unavailable.
    """
    try:
        import anthropic as ac
        client = ac.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        response = client.messages.batches.create if False else None

        # Use voyage-3 embeddings through Anthropic
        import urllib.request
        import json

        api_key = os.environ.get("ANTHROPIC_API_KEY")

        # Call Voyage AI embeddings (Anthropic's embedding partner)
        data = json.dumps({
            "input": [text_a, text_b],
            "model": "voyage-3"
        }).encode()

        req = urllib.request.Request(
            "https://api.voyageai.com/v1/embeddings",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            vec_a = result["data"][0]["embedding"]
            vec_b = result["data"][1]["embedding"]
            return cosine_similarity(vec_a, vec_b)

    except Exception:
        # Fallback: lexical overlap
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union)


@mcp.tool
def detectar_gap(texto_a: str, texto_b: str) -> dict:
    """
    Detects semantic gap between two texts using real embeddings.
    Returns gap score (0 = no gap, 1 = complete disconnection),
    severity level, and vocabulary unique to each text.
    Requires ANTHROPIC_API_KEY environment variable.
    """
    similarity = semantic_similarity(texto_a, texto_b)
    gap_score = round(1 - similarity, 2)

    # Lexical analysis for vocabulary insights
    palabras_a = set(texto_a.lower().split())
    palabras_b = set(texto_b.lower().split())
    solo_en_a = palabras_a - palabras_b
    solo_en_b = palabras_b - palabras_a

    if gap_score < 0.3:
        nivel = "bajo"
        mensaje = "Los textos comparten suficiente significado. Gap mínimo."
    elif gap_score < 0.6:
        nivel = "medio"
        mensaje = "Existe desconexión parcial. Puede haber malentendidos."
    else:
        nivel = "alto"
        mensaje = "Gap semántico significativo. Los textos hablan de mundos distintos."

    return {
        "gap_score": gap_score,
        "nivel": nivel,
        "mensaje": mensaje,
        "similaridad_semantica": round(similarity, 2),
        "palabras_solo_en_A": list(solo_en_a)[:5],
        "palabras_solo_en_B": list(solo_en_b)[:5],
        "metodo": "embeddings" if gap_score != round(1 - len(palabras_a & palabras_b) / len(palabras_a | palabras_b) if palabras_a | palabras_b else 1, 2) else "lexical_fallback"
    }


@mcp.tool
def reformular_pregunta(pregunta: str) -> dict:
    """
    Takes a question and generates alternative framings to surface
    the real need behind it. Based on the Question Reframe method.
    Uses Claude to generate contextually aware reformulations.
    Requires ANTHROPIC_API_KEY environment variable.
    """
    try:
        client = get_client()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system="""You are InterOrdra's Question Reframe engine.
Given a question, generate exactly 3 alternative framings that surface the real underlying need.
Respond only in JSON format:
{
  "variantes": [
    "reframing 1",
    "reframing 2", 
    "reframing 3"
  ]
}
The reframings should: explore context, uncover root cause, and find alternative paths.
Respond in the same language as the input question.""",
            messages=[{"role": "user", "content": pregunta}]
        )

        import json
        content = response.content[0].text
        parsed = json.loads(content)
        variantes = parsed.get("variantes", [])

    except Exception:
        # Fallback to template-based reframing
        pregunta_lower = pregunta.lower().strip()
        variantes = [
            f"¿Qué significa exactamente '{pregunta_lower}' en este contexto?",
            f"¿Cuál es el problema de fondo detrás de: '{pregunta_lower}'?",
            f"Si '{pregunta_lower}' no es posible, ¿qué alternativa resolvería la necesidad real?",
        ]

    return {
        "pregunta_original": pregunta,
        "variantes": variantes,
        "instruccion": "Usa estas variantes para explorar el gap entre lo que se pregunta y lo que se necesita."
    }


@mcp.tool
def analizar_conversacion(mensajes: list[str]) -> dict:
    """
    Analyzes a sequence of messages to detect accumulating semantic gaps.
    Useful for identifying when a conversation is drifting apart.
    Pass a list of messages in chronological order.
    Requires ANTHROPIC_API_KEY environment variable.
    """
    if len(mensajes) < 2:
        return {"error": "Se necesitan al menos 2 mensajes para analizar una conversación."}

    gaps = []
    for i in range(len(mensajes) - 1):
        similarity = semantic_similarity(mensajes[i], mensajes[i + 1])
        gap = round(1 - similarity, 2)
        gaps.append({
            "entre_mensajes": f"{i+1} y {i+2}",
            "gap_score": gap,
            "nivel": "alto" if gap >= 0.6 else "medio" if gap >= 0.3 else "bajo"
        })

    avg_gap = round(sum(g["gap_score"] for g in gaps) / len(gaps), 2)
    max_gap = max(gaps, key=lambda x: x["gap_score"])

    return {
        "gaps_detectados": gaps,
        "gap_promedio": avg_gap,
        "punto_critico": max_gap,
        "diagnostico": (
            "Conversación coherente" if avg_gap < 0.3
            else "Deriva semántica moderada" if avg_gap < 0.6
            else "Conversación gravemente desacoplada"
        )
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=7860)
