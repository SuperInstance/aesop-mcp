"""Fable data structure and generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .character import Character


@dataclass
class Fable:
    """A fable with characters, plot, moral, and stylistic metadata."""

    title: str = ""
    characters: List[Character] = field(default_factory=list)
    setting: str = ""
    plot: str = ""
    moral: str = ""
    style: str = "classic"  # classic, modern, absurdist, noir, etc.
    archetype: str = ""  # maps to the mythological archetype
    holonomy_pattern: str = ""
    maps_to: str = ""

    @property
    def summary(self) -> str:
        parts: List[str] = []
        if self.title:
            parts.append(f"# {self.title}")
        if self.setting:
            parts.append(f"Setting: {self.setting}")
        if self.characters:
            names = ", ".join(c.name for c in self.characters)
            parts.append(f"Characters: {names}")
        if self.plot:
            parts.append(self.plot)
        if self.moral:
            parts.append(f"Moral: {self.moral}")
        return "\n\n".join(parts)

    def to_dict(self) -> Dict[str, object]:
        return {
            "title": self.title,
            "archetype": self.archetype,
            "characters": [c.to_dict() for c in self.characters],
            "setting": self.setting,
            "plot": self.plot,
            "moral": self.moral,
            "style": self.style,
            "holonomy_pattern": self.holonomy_pattern,
            "maps_to": self.maps_to,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> Fable:
        chars_data = data.get("characters", [])
        characters = []
        for cd in chars_data:
            if isinstance(cd, dict):
                from .character import Archetype

                arch = cd.get("archetype", "hero")
                try:
                    archetype = Archetype(str(arch))
                except ValueError:
                    archetype = Archetype.HERO
                characters.append(
                    Character(
                        name=str(cd.get("name", "Unnamed")),
                        archetype=archetype,
                        role=str(cd.get("role", "")),
                        description=str(cd.get("description", "")),
                    )
                )
        return cls(
            title=str(data.get("title", "")),
            characters=characters,
            setting=str(data.get("setting", "")),
            plot=str(data.get("plot", "")),
            moral=str(data.get("moral", "")),
            style=str(data.get("style", "classic")),
            archetype=str(data.get("archetype", "")),
            holonomy_pattern=str(data.get("holonomy_pattern", "")),
            maps_to=str(data.get("maps_to", "")),
        )
