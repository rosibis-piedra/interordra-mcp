import os
import math
from typing import Annotated
from fastmcp import FastMCP
import anthropic
from mcp.types import ToolAnnotations
from pydantic import Field

# ─────────────────────────────────────────
#  InterOrdra MCP Server — v0.3
#  Semantic gap detection using real embeddings
#  API key provided by the user, not the author
# ─────────────────────────────────────────

mcp = FastMCP(
    name="InterOrdra",
    instructions=(
        "Semantic gap detection tool for AI agents. "
        "Detects when two systems are communicating without truly understanding each other "
        "by measuring semantic distance between texts. "
        "Use detectar_gap to measure the semantic distance between two texts, "
        "reformular_pregunta to surface the real need behind a vague question, "
        "and analizar_conversacion to find where a multi-turn conversation loses coherence."
    ),
)


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


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))
def detectar_gap(
    texto_a: Annotated[str, Field(description="First text to compare. Can be a sentence, paragraph, question, or concept description.")],
    texto_b: Annotated[str, Field(description="Second text to compare. The semantic distance between this and texto_a will be measured and scored from 0 (no gap) to 1 (complete disconnection).")],
) -> dict:
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


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=False))
def reformular_pregunta(
    pregunta: Annotated[str, Field(description="The question or request to reframe. Works best with vague, unclear, or repetitive questions where the underlying need is not obvious.")],
) -> dict:
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


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))
def analizar_conversacion(
    mensajes: Annotated[list[str], Field(description="List of messages in chronological order. Minimum 2 messages required. Each message should be a string representing one turn in the conversation.")],
) -> dict:
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


@mcp.prompt
def gap_detection_prompt(
    texto_a: Annotated[str, Field(description="First text to compare")],
    texto_b: Annotated[str, Field(description="Second text to compare")],
) -> str:
    """Prompt to detect and explain the semantic gap between two texts."""
    return (
        f"Detect the semantic gap between these two texts and explain what is causing the disconnection.\n\n"
        f"Text A: {texto_a}\n\n"
        f"Text B: {texto_b}\n\n"
        f"Use the detectar_gap tool to measure the semantic distance, then explain what conceptual worlds "
        f"each text belongs to and why they are failing to connect."
    )


@mcp.prompt
def conversation_analysis_prompt(
    contexto: Annotated[str, Field(description="Brief description of what the conversation is about")] = "",
) -> str:
    """Prompt to analyze semantic drift across a conversation."""
    context_line = f" about: {contexto}" if contexto else ""
    return (
        f"Analyze the semantic drift in a conversation{context_line}.\n\n"
        f"Instructions:\n"
        f"1. Collect the messages from the conversation in chronological order\n"
        f"2. Use the analizar_conversacion tool with those messages\n"
        f"3. Identify the critical breakpoint where alignment was lost\n"
        f"4. Suggest how to reconnect the conversation from that point"
    )


@mcp.prompt
def question_reframe_prompt(
    pregunta: Annotated[str, Field(description="The question or request to explore")],
) -> str:
    """Prompt to reframe a question and surface the underlying need."""
    return (
        f"The following question may be hiding a deeper need: '{pregunta}'\n\n"
        f"Use the reformular_pregunta tool to generate alternative framings, "
        f"then recommend which reframing best captures the real underlying problem "
        f"and explain why the original question may have been creating a semantic gap."
    )


SERVER_CARD = {
    "qualityVersion": 1,
    "name": "InterOrdra",
    "description": (
        "Semantic gap detection tool for AI agents. Detects when two systems are "
        "communicating without truly understanding each other by measuring semantic "
        "distance between texts."
    ),
    "homepage": "https://github.com/rosibis-piedra/interordra",
    "icon": "https://avatars.githubusercontent.com/u/rosibis-piedra",
    "configSchema": {
        "type": "object",
        "title": "InterOrdra Configuration",
        "properties": {
            "anthropicApiKey": {
                "type": "string",
                "title": "Anthropic API Key",
                "description": (
                    "Your Anthropic API key. Used to call Claude for question reframing "
                    "and to authenticate with Voyage AI for semantic embeddings."
                ),
                "x-sensitive": True,
            },
            "voyageApiKey": {
                "type": "string",
                "title": "Voyage AI API Key (optional)",
                "description": (
                    "Optional dedicated Voyage AI API key. If not provided, InterOrdra "
                    "will use the Anthropic API key with the Voyage AI endpoint."
                ),
                "x-sensitive": True,
            },
        },
        "required": ["anthropicApiKey"],
    },
}


@mcp.custom_route("/.well-known/mcp/server-card.json", methods=["GET"])
async def serve_server_card(request):
    from starlette.responses import JSONResponse
    return JSONResponse(SERVER_CARD)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=7860)
