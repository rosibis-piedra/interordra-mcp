from fastmcp import FastMCP

# ─────────────────────────────────────────
#  InterOrdra MCP Server — versión mínima
#  Herramienta para detección de gaps semánticos
# ─────────────────────────────────────────

mcp = FastMCP(name="InterOrdra")


@mcp.tool
def detectar_gap(texto_a: str, texto_b: str) -> dict:
    """
    Detecta si existe un gap semántico entre dos textos.
    Útil para identificar desconexiones entre lo que se pregunta
    y lo que se responde, o entre dos conceptos relacionados.
    """
    palabras_a = set(texto_a.lower().split())
    palabras_b = set(texto_b.lower().split())

    compartidas = palabras_a & palabras_b
    solo_en_a = palabras_a - palabras_b
    solo_en_b = palabras_b - palabras_a

    total = len(palabras_a | palabras_b)
    overlap = len(compartidas) / total if total > 0 else 0
    gap_score = round(1 - overlap, 2)  # 0 = sin gap, 1 = gap total

    if gap_score < 0.3:
        nivel = "bajo"
        mensaje = "Los textos comparten suficiente vocabulario. Gap mínimo."
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
        "palabras_solo_en_A": list(solo_en_a)[:5],
        "palabras_solo_en_B": list(solo_en_b)[:5],
    }


@mcp.tool
def reformular_pregunta(pregunta: str) -> dict:
    """
    Toma una pregunta y genera versiones alternativas para cerrar
    posibles gaps de comprensión. Basado en el método Question Reframe.
    """
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


if __name__ == "__main__":
    mcp.run()
