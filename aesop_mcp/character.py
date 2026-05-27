"""Character archetypes with trait systems for fable generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Archetype(str, Enum):
    """Core character archetypes drawn from classical mythology."""

    TRICKSTER = "trickster"
    SAGE = "sage"
    FOOL = "fool"
    HERO = "hero"
    OUTCAST = "outcast"
    CREATOR = "creator"
    RULER = "ruler"
    CAREGIVER = "caregiver"
    EXPLORER = "explorer"
    REBEL = "rebel"


@dataclass
class Trait:
    """A character trait with a name, intensity (0-10), and optional description."""

    name: str
    intensity: int = 5
    description: str = ""

    def __post_init__(self) -> None:
        if not 0 <= self.intensity <= 10:
            raise ValueError(f"Trait intensity must be 0-10, got {self.intensity}")


# Default trait profiles keyed by archetype
_ARCHETYPE_TRAITS: Dict[Archetype, List[Dict[str, object]]] = {
    Archetype.TRICKSTER: [
        {"name": "cunning", "intensity": 9},
        {"name": "deception", "intensity": 7},
        {"name": "wit", "intensity": 8},
        {"name": "self_interest", "intensity": 7},
        {"name": "adaptability", "intensity": 8},
    ],
    Archetype.SAGE: [
        {"name": "wisdom", "intensity": 10},
        {"name": "patience", "intensity": 8},
        {"name": "foresight", "intensity": 9},
        {"name": "restraint", "intensity": 7},
        {"name": "detachment", "intensity": 6},
    ],
    Archetype.FOOL: [
        {"name": "ignorance", "intensity": 8},
        {"name": "overconfidence", "intensity": 7},
        {"name": "stubbornness", "intensity": 6},
        {"name": "simplicity", "intensity": 7},
        {"name": "luck", "intensity": 5},
    ],
    Archetype.HERO: [
        {"name": "courage", "intensity": 9},
        {"name": "determination", "intensity": 8},
        {"name": "self_sacrifice", "intensity": 7},
        {"name": "honor", "intensity": 8},
        {"name": "strength", "intensity": 7},
    ],
    Archetype.OUTCAST: [
        {"name": "isolation", "intensity": 8},
        {"name": "resilience", "intensity": 7},
        {"name": "bitterness", "intensity": 6},
        {"name": "independence", "intensity": 8},
        {"name": "perspective", "intensity": 7},
    ],
    Archetype.CREATOR: [
        {"name": "vision", "intensity": 9},
        {"name": "obsession", "intensity": 7},
        {"name": "craft", "intensity": 8},
        {"name": "pride", "intensity": 6},
        {"name": "innovation", "intensity": 9},
    ],
    Archetype.RULER: [
        {"name": "authority", "intensity": 9},
        {"name": "control", "intensity": 8},
        {"name": "responsibility", "intensity": 7},
        {"name": "pride", "intensity": 7},
        {"name": "rigidity", "intensity": 6},
    ],
    Archetype.CAREGIVER: [
        {"name": "compassion", "intensity": 9},
        {"name": "generosity", "intensity": 8},
        {"name": "selflessness", "intensity": 8},
        {"name": "patience", "intensity": 7},
        {"name": "protectiveness", "intensity": 7},
    ],
    Archetype.EXPLORER: [
        {"name": "curiosity", "intensity": 9},
        {"name": "restlessness", "intensity": 7},
        {"name": "courage", "intensity": 7},
        {"name": "independence", "intensity": 8},
        {"name": "adaptability", "intensity": 7},
    ],
    Archetype.REBEL: [
        {"name": "defiance", "intensity": 9},
        {"name": "idealism", "intensity": 7},
        {"name": "courage", "intensity": 8},
        {"name": "impatience", "intensity": 6},
        {"name": "charisma", "intensity": 7},
    ],
}


@dataclass
class Character:
    """A fable character with an archetype, name, and trait profile."""

    name: str
    archetype: Archetype
    traits: List[Trait] = field(default_factory=list)
    role: str = ""  # protagonist, antagonist, mentor, etc.
    description: str = ""

    def __post_init__(self) -> None:
        if not self.traits:
            self.traits = self._default_traits()

    def _default_traits(self) -> List[Trait]:
        raw = _ARCHETYPE_TRAITS.get(self.archetype, [])
        return [Trait(**t) for t in raw]  # type: ignore[arg-type]

    @property
    def dominant_trait(self) -> Optional[Trait]:
        if not self.traits:
            return None
        return max(self.traits, key=lambda t: t.intensity)

    @property
    def weakness(self) -> Optional[Trait]:
        """Return the trait most likely to be the character's downfall (lowest intensity)."""
        if not self.traits:
            return None
        return min(self.traits, key=lambda t: t.intensity)

    def conflicts_with(self, other: Character) -> bool:
        """Two characters conflict if their dominant traits are opposed."""
        opposites = {
            "cunning": "honor",
            "wisdom": "ignorance",
            "courage": "stubbornness",
            "control": "independence",
            "compassion": "self_interest",
            "authority": "defiance",
            "vision": "simplicity",
            "patience": "impatience",
        }
        if not self.dominant_trait or not other.dominant_trait:
            return False
        dn = self.dominant_trait.name
        on = other.dominant_trait.name
        return opposites.get(dn) == on or opposites.get(on) == dn

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "archetype": self.archetype.value,
            "role": self.role,
            "description": self.description,
            "traits": [{"name": t.name, "intensity": t.intensity} for t in self.traits],
            "dominant_trait": self.dominant_trait.name if self.dominant_trait else None,
        }
