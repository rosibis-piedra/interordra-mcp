# InterOrdra MCP Server

**Semantic gap detection tool for AI agents.**

InterOrdra detects when two systems are talking without listening to each other — measuring the semantic distance between texts and surfacing the invisible disconnections that cause miscommunication, misalignment, and failed coordination.

Built as an MCP server so any agent can use it.

---

## Requirements

- Python 3.10+
- `ANTHROPIC_API_KEY` environment variable set with your own key

```bash
pip install fastmcp anthropic
```

> **Note:** InterOrdra uses your own Anthropic API key. The author does not pay for your usage.

---

## Tools

### `detectar_gap`
Detects semantic gaps between two texts using real embeddings (Voyage AI via Anthropic). Returns a gap score, severity level, and vocabulary unique to each text.

```json
{
  "texto_a": "the server is not responding to network requests",
  "texto_b": "I need the team to understand my product vision"
}
```

**Returns:**
```json
{
  "gap_score": 0.94,
  "nivel": "alto",
  "mensaje": "Gap semántico significativo. Los textos hablan de mundos distintos.",
  "similaridad_semantica": 0.06,
  "palabras_solo_en_A": ["servidor", "red", "solicitudes"],
  "palabras_solo_en_B": ["visión", "producto", "equipo"],
  "metodo": "embeddings"
}
```

---

### `reformular_pregunta`
Takes a question and generates three alternative framings using Claude to surface the real need behind it. Based on the Question Reframe method.

```json
{
  "pregunta": "why doesn't anyone understand me"
}
```

**Returns:**
```json
{
  "pregunta_original": "why doesn't anyone understand me",
  "variantes": [
    "What specific communication breakdown is happening in your current context?",
    "What would it look like if someone truly understood you — what would change?",
    "Which part of your message consistently gets lost or misinterpreted?"
  ],
  "instruccion": "Usa estas variantes para explorar el gap entre lo que se pregunta y lo que se necesita."
}
```

---

### `analizar_conversacion`
Analyzes a sequence of messages to detect accumulating semantic gaps. Identifies where a conversation starts drifting apart.

```json
{
  "mensajes": [
    "We need to improve system performance",
    "I think we should hire more engineers",
    "The budget for Q3 is already allocated",
    "Can we talk about team morale instead?"
  ]
}
```

**Returns:**
```json
{
  "gaps_detectados": [
    {"entre_mensajes": "1 y 2", "gap_score": 0.45, "nivel": "medio"},
    {"entre_mensajes": "2 y 3", "gap_score": 0.71, "nivel": "alto"},
    {"entre_mensajes": "3 y 4", "gap_score": 0.83, "nivel": "alto"}
  ],
  "gap_promedio": 0.66,
  "punto_critico": {"entre_mensajes": "3 y 4", "gap_score": 0.83},
  "diagnostico": "Conversación gravemente desacoplada"
}
```

---

## Connect to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "interordra": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Replace `/path/to/server.py` with the actual path and add your own API key.

Restart Claude Desktop. InterOrdra will appear as an available tool.

---

## Use cases

- Detect misalignment between a question and its answer
- Identify when two teams are operating in disconnected conceptual frameworks
- Surface semantic gaps in multi-agent pipelines
- Analyze conversations to find where the thread breaks
- Reframe questions to uncover the real underlying need

---

## Background

InterOrdra emerged from a pattern: seeing where two systems are broadcasting on completely different frequencies — technically communicating, actually disconnected.

The name comes from *inter* (between) + *ordra* (order/structure) — the space between ordered systems where gaps live.

**Full project:** [github.com/rosibis-piedra/interordra](https://github.com/rosibis-piedra/interordra)

---

## Author

**Rosibis Piedra**
AI Software Engineer · Costa Rica
[github.com/rosibis-piedra](https://github.com/rosibis-piedra)

---

## License

MIT
