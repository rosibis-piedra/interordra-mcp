---
title: InterOrdra MCP
emoji: 🔍
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
license: mit
short_description: Semantic gap detection tool for AI agents
---

# InterOrdra MCP Server

**Semantic gap detection tool for AI agents.**

InterOrdra detects when two systems are talking without listening to each other — measuring the semantic distance between texts and surfacing the invisible disconnections that cause miscommunication, misalignment, and failed coordination.

Built as an MCP server so any agent can use it.

---

## When to use InterOrdra

**Call `detectar_gap` when:**
- A question and its answer seem disconnected or off-topic
- Two teams are not reaching agreement despite communicating
- You need to verify if two concepts belong to the same semantic space
- A user's request and the system's response are misaligned
- You suspect a conversation is failing due to conceptual distance, not lack of information

**Call `reformular_pregunta` when:**
- A question is too vague to answer well
- The real need behind a request is unclear
- A user keeps asking the same thing in different ways without getting satisfaction
- You want to surface the underlying problem before answering

**Call `analizar_conversacion` when:**
- A multi-turn conversation is drifting and losing coherence
- You need to find the exact point where alignment broke down
- An agent pipeline is producing inconsistent outputs across turns
- You want to diagnose why a negotiation or discussion failed

---

## Tools

### `detectar_gap`
Detects semantic gaps between two texts using real embeddings. Returns a gap score (0 = no gap, 1 = complete disconnection), severity level, and vocabulary unique to each text.

**Input:**
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

**Gap score interpretation:**
- `0.0 – 0.3` → Low gap. Texts share enough meaning.
- `0.3 – 0.6` → Medium gap. Partial disconnection. Misunderstandings likely.
- `0.6 – 1.0` → High gap. Texts operate in completely different conceptual worlds.

---

### `reformular_pregunta`
Takes a question and generates three alternative framings using Claude to surface the real need behind it. Based on the Question Reframe method.

**Input:**
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
  "instruccion": "Use these variants to explore the gap between what is asked and what is needed."
}
```

---

### `analizar_conversacion`
Analyzes a sequence of messages to detect accumulating semantic gaps. Identifies where a conversation starts drifting apart.

**Input:**
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

## Requirements

- Python 3.10+
- `ANTHROPIC_API_KEY` environment variable set with your own key

```bash
pip install fastmcp anthropic
```

> **Note:** InterOrdra uses your own Anthropic API key. The author does not pay for your usage.

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

Replace `/path/to/server.py` with the actual path. Restart Claude Desktop — InterOrdra will appear as an available tool.

---

## Connect via Smithery

Available at [smithery.ai](https://smithery.ai/server/interordra-mcp--rosibisdev)

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