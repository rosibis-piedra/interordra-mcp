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

# InterOrdra MCP

[![smithery badge](https://smithery.ai/badge/rosibisdev/interordra-mcp)](https://smithery.ai/servers/rosibisdev/interordra-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![M8ven Score](https://m8ven.ai/badge/mcp/rosibis-piedra-interordra-mcp-0mmpvd)](https://m8ven.ai/mcp/rosibis-piedra-interordra-mcp-0mmpvd)

**Measure semantic distance between texts. Detect misalignment before it becomes a problem.**

InterOrdra is an MCP server that tells you — with a number — how far apart two pieces of text are conceptually. Not just keyword overlap: real semantic distance using embeddings.

Built for AI agents, pipelines, and developers who need to know when a conversation, a retrieval, or a response is failing silently.

---

## The problem it solves

Two things can be syntactically connected but semantically worlds apart:

- A user asks about X. Your agent responds about Y. Nobody notices.
- Your RAG pipeline retrieves documents. They don't actually answer the query. The LLM hallucinates to fill the gap.
- A negotiation goes on for hours. The parties are never talking about the same thing.
- A user rephrases the same question 5 times. The system keeps missing the real need.

InterOrdra surfaces these gaps. It gives you a score from 0 (fully aligned) to 1 (completely disconnected), the severity level, and the vocabulary unique to each side.

---

## Connect via Smithery (recommended)

No setup required. Works with any MCP-compatible client.

[![Connect on Smithery](https://smithery.ai/badge/rosibisdev/interordra-mcp)](https://smithery.ai/servers/rosibisdev/interordra-mcp)

You'll need your own `ANTHROPIC_API_KEY`. Smithery will prompt you for it on connect.

---

## Use cases

| Scenario | Tool to call |
|---|---|
| Check if an LLM answer is relevant to the question | `detectar_gap` |
| Validate RAG retrieval — does the doc actually answer the query? | `detectar_gap` |
| Two agents in a pipeline producing disconnected outputs | `detectar_gap` |
| User keeps rephrasing the same question unsatisfied | `reformular_pregunta` |
| Find the real need behind a vague request | `reformular_pregunta` |
| Multi-turn conversation drifting and losing coherence | `analizar_conversacion` |
| Diagnose why a negotiation or discussion failed | `analizar_conversacion` |
| Detect misalignment between two team members' messages | `analizar_conversacion` |

---

## When to call each tool

**Call `detectar_gap` when:**
- A question and its answer seem off-topic or disconnected
- You need a numeric score for semantic similarity between two texts
- You're building a relevance filter for retrieval-augmented generation
- Two concepts need to be verified as belonging to the same semantic space

**Call `reformular_pregunta` when:**
- A question is too vague to answer well
- A user keeps asking the same thing without getting satisfaction
- You need to surface the underlying problem before responding

**Call `analizar_conversacion` when:**
- A multi-turn conversation is drifting and losing coherence
- You need to find the exact turn where alignment broke down
- An agent pipeline is producing inconsistent outputs across turns

---

## Tools

### `detectar_gap`

Measures semantic distance between two texts using embeddings. Returns a gap score, severity level, and the vocabulary unique to each text.

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

**Gap score:**
- `0.0 – 0.3` → Low. Texts share enough meaning.
- `0.3 – 0.6` → Medium. Partial disconnection. Misunderstandings likely.
- `0.6 – 1.0` → High. Texts operate in completely different conceptual worlds.

---

### `reformular_pregunta`

Takes a question and returns three alternative framings that surface the real need behind it. Uses Claude.

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

Analyzes a sequence of messages to detect accumulating semantic gaps. Finds where a conversation starts drifting apart.

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

## Self-host

**Requirements:** Python 3.10+ · Your own `ANTHROPIC_API_KEY`

```bash
pip install fastmcp anthropic
python server.py
```

**Claude Desktop** — add to `claude_desktop_config.json`:

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

> InterOrdra uses your own Anthropic API key. The author does not pay for your usage.

---

## Background

InterOrdra emerged from a pattern: two systems broadcasting on completely different frequencies — technically communicating, actually disconnected.

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
