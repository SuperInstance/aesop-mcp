"""MoralEngine — extract and match morals from stories."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# Canonical moral templates indexed by theme
MORAL_TEMPLATES: Dict[str, Dict[str, str]] = {
    "hubris": {
        "moral": "Overreach leads to downfall.",
        "archetype": "icarus",
        "keywords": ["overconfident", "pride", "hubris", "too far", "too high", "arrogant", "overreach"],
    },
    "perseverance": {
        "moral": "The constraint graph has a cycle that can't flatten. Change the graph, not the push.",
        "archetype": "sisyphus",
        "keywords": ["repeat", "cycle", "persist", "stuck", "grind", "endless", "futile"],
    },
    "communication": {
        "moral": "Consensus fails at the protocol layer, not the math layer.",
        "archetype": "tower_of_babel",
        "keywords": ["language", "coordinate", "misunderstand", "protocol", "translate", " babel"],
    },
    "renewal": {
        "moral": "The collapse WAS the consensus event. It couldn't happen without breaking first.",
        "archetype": "phoenix",
        "keywords": ["collapse", "rebuild", "renew", "rebirth", "ashes", "recover", "reorganize"],
    },
    "identity": {
        "moral": "If every tile is replaced one by one, is it the same fleet? Yes — the connection stays flat.",
        "archetype": "theseus_ship",
        "keywords": ["replace", "identity", "transform", "gradual", "incremental", "same"],
    },
    "hidden_truth": {
        "moral": "The constraint field carries truth even when every measurement is biased.",
        "archetype": "arachne",
        "keywords": ["weave", "hidden", "bias", "reveal", "tapestry", "fabric", "gate"],
    },
    "deliberation": {
        "moral": "Sometimes non-consensus IS the strategy. Persistent deliberation prevents premature agreement.",
        "archetype": "penelopes_web",
        "keywords": ["stall", "delay", "deliberate", "undo", "oscillate", "unweave", "strategy"],
    },
    "sacrifice": {
        "moral": "Some constraints can never be satisfied. You live with the holonomy.",
        "archetype": "prometheus",
        "keywords": ["sacrifice", "steal", "fire", "permanent", "eternal", "undecidable", "open"],
    },
    "introspection": {
        "moral": "Zero holonomy on an isolated cycle is not consensus. It's solipsism.",
        "archetype": "narcissus",
        "keywords": ["reflection", "echo", "mirror", "self", "narcissist", "isolated", "feedback loop"],
    },
    "conformity": {
        "moral": "If your consensus mechanism never finds disagreement, you're mutilating the data.",
        "archetype": "procrustes",
        "keywords": ["force", "fit", "template", "mold", "stretch", "cut", "conform", "suppress"],
    },
}

# Additional standalone morals for general matching
EXTRA_MORALS: List[str] = [
    "Slow and steady wins the race.",
    "Appearances can be deceiving.",
    "United we stand, divided we fall.",
    "The early bird catches the worm.",
    "Don't count your chickens before they hatch.",
    "A stitch in time saves nine.",
    "The wolf in sheep's clothing reveals that trust must be earned, not assumed.",
    "The boy who cried wolf learned that credibility, once lost, is hard to regain.",
]


@dataclass
class MoralMatch:
    """A moral matched to a story or problem."""

    theme: str
    moral: str
    archetype: str
    relevance: float  # 0.0 to 1.0
    matched_keywords: List[str] = field(default_factory=list)


class MoralEngine:
    """Extract and match morals from stories and problems."""

    def __init__(self, templates: Optional[Dict[str, Dict[str, str]]] = None) -> None:
        self.templates = templates or MORAL_TEMPLATES

    def extract_morals(self, text: str, top_n: int = 5) -> List[MoralMatch]:
        """Extract relevant morals from text by keyword matching."""
        text_lower = text.lower()
        matches: List[MoralMatch] = []

        for theme, info in self.templates.items():
            keywords = info["keywords"]
            matched = [kw for kw in keywords if kw in text_lower]
            if matched:
                relevance = min(len(matched) / max(len(keywords), 1), 1.0)
                matches.append(
                    MoralMatch(
                        theme=theme,
                        moral=info["moral"],
                        archetype=info["archetype"],
                        relevance=relevance,
                        matched_keywords=matched,
                    )
                )

        matches.sort(key=lambda m: m.relevance, reverse=True)
        return matches[:top_n]

    def find_moral(self, text: str) -> Optional[MoralMatch]:
        """Find the single best moral for a text."""
        results = self.extract_morals(text, top_n=1)
        return results[0] if results else None

    def extract_moral_sentences(self, text: str) -> List[str]:
        """Extract sentences that look like moral statements from text."""
        moral_patterns = [
            r"(?i)therefore,?\s+(.+?)[.!?]",
            r"(?i)the moral (?:of the story )?is:?\s*(.+?)[.!?]",
            r"(?i)we (?:can |may )?learn (?:that|how)\s+(.+?)[.!?]",
            r"(?i)(?:one |a )?lesson (?:here |to be learned )?is:?\s*(.+?)[.!?]",
            r"(?i)(?:thus|hence|so),?\s+(.+?)[.!?]",
        ]
        sentences: List[str] = []
        for pattern in moral_patterns:
            for match in re.finditer(pattern, text):
                sentence = match.group(0).strip()
                if sentence not in sentences:
                    sentences.append(sentence)
        return sentences

    def compare_morals(self, moral_a: str, moral_b: str) -> float:
        """Compare two moral statements for similarity (simple word overlap)."""
        words_a = set(moral_a.lower().split())
        words_b = set(moral_b.lower().split())
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "shall", "can",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "it", "its", "not", "no", "but", "and", "or", "if", "that",
        }
        filtered_a = words_a - stopwords
        filtered_b = words_b - stopwords
        if not filtered_a or not filtered_b:
            return 0.0
        intersection = filtered_a & filtered_b
        union = filtered_a | filtered_b
        return len(intersection) / len(union)

    def converge(self, morals: List[str], threshold: float = 0.3) -> List[List[str]]:
        """Find clusters of similar morals (convergence groups)."""
        clusters: List[List[str]] = []
        assigned: set[int] = set()

        for i, m1 in enumerate(morals):
            if i in assigned:
                continue
            cluster = [m1]
            assigned.add(i)
            for j, m2 in enumerate(morals):
                if j in assigned:
                    continue
                if self.compare_morals(m1, m2) >= threshold:
                    cluster.append(m2)
                    assigned.add(j)
            if len(cluster) > 1:
                clusters.append(cluster)

        return clusters

    def negative_space(self, text: str, morals: List[str]) -> Dict[str, object]:
        """Find terms in the text not covered by any matched moral."""
        text_words = set(text.lower().split())
        moral_words: set[str] = set()
        for m in morals:
            moral_words.update(m.lower().split())

        stopwords = {
            "the", "and", "that", "this", "with", "from", "for", "have",
            "has", "not", "but", "are", "its", "was", "can", "all", "some",
        }
        uncovered = sorted(
            w for w in text_words - moral_words if len(w) > 3 and w not in stopwords
        )

        return {
            "uncovered_terms": uncovered[:10],
            "coverage": len(text_words & moral_words) / max(len(text_words), 1),
            "insight": (
                f"{len(uncovered)} terms in the problem aren't addressed by the matched morals. "
                f"The truth may live in the gap between what these stories cover."
            ),
        }
