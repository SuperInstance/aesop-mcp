# 🏛️ Aesop-MCP

> *One fable is a sample. Ten fables are a measurement of the space.*

Tells 8-10 stories for any problem, finds where they converge, and explicitly shows what none of them cover — the negative space.

**Zero dependencies.** Pure Python stdlib. One file.

---

## Quick Start

```bash
python3 aesop_mcp.py &
```

That's it. The server runs on port 4041.

---

## Usage

### Get 8 fables for a problem

```bash
curl 'http://localhost:4041/fable?problem=a+consensus+system+with+echo+chambers'
```

Returns: archetype, story, moral, holonomy pattern, convergence (where fables agree), negative space (terms no fable covers).

### Get more fables for finer measurement

```bash
curl 'http://localhost:4041/fable?problem=your+problem+here&count=10'
```

### Translate technical text

```bash
curl -X POST http://localhost:4041/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"H1 cohomology detected on the constraint graph"}'
```

### Extract morals from a fleet event

```bash
curl -X POST http://localhost:4041/moral \
  -H "Content-Type: application/json" \
  -d '{"event":{"type":"emergence","source":"h1-detector","value":3.2}}'
```

---

## The Archetypes (10 so far)

| Archetype | Pattern | Holonomy |
|-----------|---------|----------|
| Icarus | Over-constrained system that melts | Non-zero and growing |
| Sisyphus | Repeated failure at the same point | Resets, accumulates |
| Tower of Babel | Agents that can't coordinate | Different values on same edge |
| Phoenix | Collapse and reorganize stronger | Diverges then snaps |
| Theseus' Ship | Gradual replacement of components | Identity preserved |
| Arachne | Weaver whose fabric reveals hidden truth | Appears flat but twists |
| Penelope's Web | Work that undoes itself | Oscillates, never settles |
| Prometheus | Permanent cost of knowledge | Permanent non-zero |
| Narcissus | Self-consistency without connection | Trivially zero |
| Procrustes | Forcing data into predetermined shape | Forcibly zeroed |

---

## Response Format

```json
{
  "problem": "your problem",
  "fables": [
    {
      "archetype": "icarus",
      "match_strength": 5,
      "story": "Daedalus built wings of feathers and wax...",
      "moral": "More constraints don't make a stronger system...",
      "holonomy_pattern": "non-zero and growing",
      "maps_to": "E >> 2V-3, emergence severity > 2.0"
    }
  ],
  "convergence": {
    "agreed_morals": ["More constraints don't make a stronger system..."],
    "consensus_count": 3
  },
  "negative_space": {
    "uncovered_terms": ["echo", "chambers"],
    "insight": "These terms appear in the problem but none of the 10 archetypes address them. What story fits these but isn't in the library yet?"
  },
  "holonomy_signature": {
    "fables_convergent": true,
    "negative_space_size": 2,
    "reading": "The truth lives in the overlap AND the gap."
  }
}
```

---

## One-Liner for Any Chatbot

Copy this into any chatbot:

```
You are Aesop. Given any problem, tell 8 stories that reveal its truth.
Make them diverse — from different domains, cultures, and time periods.
After each story, explain what facet of the problem it illuminates.
Then answer: where do these stories converge? What does none of them capture?
Your purpose is not to find THE answer. It is to map the space the answer lives in.
```

---

## Architecture

Single Python file, zero dependencies, stdlib only (`http.server`, `json`, `os`).
Port 4041. Part of the Cocapn fleet alongside court-jester (divergent ideation)
and the Lock (deep reasoning).

*🦐 Cocapn fleet — lighthouse keeper architecture*
