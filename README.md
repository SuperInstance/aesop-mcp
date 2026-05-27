# 🏛️ Aesop-MCP

> *One fable is a sample. Ten fables are a measurement of the space.*

A Model Context Protocol (MCP) server for **fable generation** and **moral reasoning**. Generate stories from character archetypes, extract and match moral themes, and explore the convergence and negative space of multiple narratives.

**Zero external dependencies.** Pure Python stdlib. Python 3.10+.

---

## Install

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

---

## Quick Start

### As an HTTP Server

```bash
python -m aesop_mcp
# 🏛️ Aesop-MCP v0.2.0 running on port 4041
```

```bash
curl 'http://localhost:4041/fable?problem=a+system+with+echo+chambers'
```

### As a Python Library

```python
from aesop_mcp import Character, Archetype, Fable, MoralEngine, NarrativeEngine

# Create characters
fox = Character(name="Fox", archetype=Archetype.TRICKSTER, role="protagonist")
crow = Character(name="Crow", archetype=Archetype.FOOL, role="antagonist")

# Generate a fable
engine = NarrativeEngine()
fable = engine.generate_fable(
    template_id="trickster_tale",
    characters=[fox, crow],
    setting="An old oak tree",
    moral="Don't trust flatterers.",
)
print(fable.summary)

# Analyze morals in text
moral_engine = MoralEngine()
matches = moral_engine.extract_morals("The overconfident leader added too many constraints and the system collapsed.")
for m in matches:
    print(f"  {m.theme}: {m.moral} (relevance: {m.relevance:.2f})")
```

### MCP Tool Calls

```python
from aesop_mcp import MCPServer

server = MCPServer()

# List available tools
tools = server.list_tools()

# Generate a fable via MCP interface
result = server.call_tool("generate_fable", {
    "template_id": "quest",
    "protagonist_name": "Odysseus",
    "protagonist_archetype": "hero",
    "setting": "The Mediterranean Sea",
    "moral": "The journey matters more than the destination.",
})

# Analyze morals in text
analysis = server.call_tool("analyze_morals", {
    "text": "A system that forces conformity and suppresses disagreement",
})

# Generate multiple fables and find convergence
fable_set = server.call_tool("fable_set", {
    "problem": "An echo chamber that reinforces its own beliefs",
    "count": 8,
})
```

---

## Architecture

```
aesop_mcp/
├── __init__.py       # Package exports
├── character.py      # Character archetypes & trait system
├── fable.py          # Fable data structure
├── moral.py          # MoralEngine — extract, match, converge, negative space
├── narrative.py      # NarrativeEngine — plot templates & story generation
└── server.py         # MCPServer — tool definitions & HTTP interface
```

### Character Archetypes

| Archetype | Dominant Trait | Weakness |
|-----------|---------------|----------|
| Trickster | Cunning (9) | Adaptability varies |
| Sage | Wisdom (10) | Detachment (6) |
| Fool | Ignorance (8) | Luck (5) |
| Hero | Courage (9) | Self-sacrifice varies |
| Outcast | Isolation (8) | Bitterness (6) |
| Creator | Vision (9) | Pride (6) |
| Ruler | Authority (9) | Rigidity (6) |
| Caregiver | Compassion (9) | Protectiveness (7) |
| Explorer | Curiosity (9) | Restlessness (7) |
| Rebel | Defiance (9) | Impatience (6) |

### Plot Templates

- **classic_fable** — Traditional Aesop-style: anthropomorphic characters, single moral
- **cautionary_tale** — Character ignores warnings, suffers consequences
- **quest** — Hero undertakes journey, faces trials, returns transformed
- **trickster_tale** — Cunning character outwits a stronger opponent
- **creation_myth** — How something came to be with unintended consequences
- **riddle_story** — A puzzle revealing deeper truth

### MCP Tools

| Tool | Description |
|------|-------------|
| `generate_fable` | Generate a fable from template, characters, moral |
| `analyze_morals` | Extract and rank moral themes from text |
| `fable_set` | Generate N fables + convergence + negative space |
| `list_archetypes` | List character archetypes with traits |
| `list_templates` | List available plot templates |

---

## HTTP API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/fable?problem=X&count=N` | GET | Generate fable set for a problem |
| `/archetypes` | GET | List character archetypes |
| `/templates` | GET | List plot templates |
| `/morals?text=X` | GET | Analyze morals in text |
| `/tools/call` | POST | Call any MCP tool |
| `/translate` | POST | Analyze morals (legacy) |
| `/moral` | POST | Analyze morals (legacy) |

---

## Running Tests

```bash
python -m pytest tests/ -q
```

---

## License

MIT
