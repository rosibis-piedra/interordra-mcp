# InterOrdra MCP Server

**Semantic gap detection tool for AI agents.**

InterOrdra detects when two systems are talking without listening to each other — measuring the semantic distance between texts and surfacing the invisible disconnections that cause miscommunication, misalignment, and failed coordination.

Built as an MCP server so any agent can use it.

---

## Tools

### `detectar_gap`
Detects semantic gaps between two texts. Returns a gap score (0 = no gap, 1 = complete disconnection), severity level, and the vocabulary unique to each text.

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
  "palabras_solo_en_A": ["servidor", "red", "solicitudes"],
  "palabras_solo_en_B": ["visión", "producto", "equipo"]
}
```

---

### `reformular_pregunta`
Takes a question and generates three alternative framings to surface the real need behind it. Based on the Question Reframe method.

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
    "What does 'why doesn't anyone understand me' mean exactly in this context?",
    "What is the underlying problem behind: 'why doesn't anyone understand me'?",
    "If 'why doesn't anyone understand me' is not solvable, what alternative would address the real need?"
  ]
}
```

---

## Installation

**Requirements:** Python 3.10+

```bash
pip install fastmcp
```

---

## Connect to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "interordra": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

Replace `/path/to/server.py` with the actual path where you saved the file.

Restart Claude Desktop. InterOrdra will appear as an available tool.

---

## Use cases

- Detect misalignment between a question and its answer
- Identify when two teams are operating in disconnected conceptual frameworks
- Surface semantic gaps in multi-agent pipelines
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
