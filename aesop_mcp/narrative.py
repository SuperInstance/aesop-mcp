"""NarrativeEngine — story templates and plot structures for fable generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from .character import Archetype, Character
from .fable import Fable


class PlotStage(str, Enum):
    """Standard narrative arc stages."""

    EXPOSITION = "exposition"
    INCITING_INCIDENT = "inciting_incident"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"


@dataclass
class PlotPoint:
    """A single point in a narrative arc."""

    stage: PlotStage
    description: str
    characters_involved: List[str] = field(default_factory=list)


# Built-in story templates
STORY_TEMPLATES: Dict[str, Dict[str, str]] = {
    "classic_fable": {
        "name": "Classic Fable",
        "description": "Traditional Aesop-style: anthropomorphic animals, single clear moral.",
        "structure": "exposition → conflict → trick/reversal → moral",
        "style": "classic",
    },
    "cautionary_tale": {
        "name": "Cautionary Tale",
        "description": "Character ignores warnings, suffers consequences.",
        "structure": "warning → disregard → escalating trouble → downfall → lesson",
        "style": "classic",
    },
    "quest": {
        "name": "Quest Narrative",
        "description": "Hero undertakes journey, faces trials, returns transformed.",
        "structure": "call → trials → abyss → transformation → return",
        "style": "epic",
    },
    "trickster_tale": {
        "name": "Trickster Tale",
        "description": "Cunning character outwits a stronger opponent.",
        "structure": "disparity → clever plan → execution → reversal → moral",
        "style": "classic",
    },
    "creation_myth": {
        "name": "Creation Myth",
        "description": "How something came to be, often with unintended consequences.",
        "structure": "void → creation → unintended consequence → adaptation → world as it is",
        "style": "mythic",
    },
    "riddle_story": {
        "name": "Riddle Story",
        "description": "A puzzle that reveals deeper truth when solved.",
        "structure": "mystery → attempts → insight → solution → wisdom",
        "style": "philosophical",
    },
}

# Plot arc templates defining stage descriptions
PLOT_ARCS: Dict[str, List[Tuple[PlotStage, str]]] = {
    "classic_fable": [
        (PlotStage.EXPOSITION, "Introduce {protagonist} in {setting}. Establish their character and situation."),
        (PlotStage.INCITING_INCIDENT, "{protagonist} encounters {conflict}, typically involving {antagonist}."),
        (PlotStage.RISING_ACTION, "{protagonist} attempts to deal with {conflict}. Complications arise."),
        (PlotStage.CLIMAX, "A decisive moment — {protagonist}'s key trait ({dominant_trait}) is tested."),
        (PlotStage.RESOLUTION, "The outcome reveals: {moral}"),
    ],
    "cautionary_tale": [
        (PlotStage.EXPOSITION, "{protagonist} lives in {setting}. A wise {mentor} warns them about {danger}."),
        (PlotStage.INCITING_INCIDENT, "{protagonist} ignores the warning, driven by {dominant_trait}."),
        (PlotStage.RISING_ACTION, "Consequences escalate. Each attempt to fix things makes it worse."),
        (PlotStage.CLIMAX, "{protagonist} faces the full consequence of their disregard."),
        (PlotStage.FALLING_ACTION, "The damage is done. {protagonist} reflects on what went wrong."),
        (PlotStage.RESOLUTION, "Moral: {moral}"),
    ],
    "quest": [
        (PlotStage.EXPOSITION, "{protagonist} receives a call to action in {setting}."),
        (PlotStage.INCITING_INCIDENT, "The quest is set: {quest_goal}. {protagonist} must leave home."),
        (PlotStage.RISING_ACTION, "Trials test {protagonist}'s {dominant_trait} and resolve."),
        (PlotStage.CLIMAX, "The greatest challenge. {protagonist} must sacrifice something dear."),
        (PlotStage.FALLING_ACTION, "Victory, but at a cost. {protagonist} is changed."),
        (PlotStage.RESOLUTION, "Return with wisdom: {moral}"),
    ],
    "trickster_tale": [
        (PlotStage.EXPOSITION, "{antagonist} holds power over {protagonist} in {setting}."),
        (PlotStage.INCITING_INCIDENT, "{protagonist} devises a clever scheme."),
        (PlotStage.RISING_ACTION, "The plan unfolds. {antagonist} begins to fall for it."),
        (PlotStage.CLIMAX, "The trick is revealed. {antagonist} is outwitted."),
        (PlotStage.RESOLUTION, "Moral: {moral}"),
    ],
}


class NarrativeEngine:
    """Generate fable narratives from characters and plot structures."""

    def __init__(self) -> None:
        self.templates = STORY_TEMPLATES
        self.arcs = PLOT_ARCS

    def list_templates(self) -> List[Dict[str, str]]:
        return [
            {"id": k, **v} for k, v in self.templates.items()
        ]

    def generate_outline(
        self,
        template_id: str,
        characters: List[Character],
        setting: str = "",
        moral: str = "",
    ) -> List[PlotPoint]:
        """Generate a plot outline from a template and characters."""
        if template_id not in self.arcs:
            raise ValueError(
                f"Unknown template '{template_id}'. "
                f"Available: {', '.join(self.arcs.keys())}"
            )

        arc = self.arcs[template_id]
        protagonist = characters[0] if characters else None
        antagonist = characters[1] if len(characters) > 1 else None
        mentor = characters[2] if len(characters) > 2 else None

        substitutions = {
            "protagonist": protagonist.name if protagonist else "the hero",
            "antagonist": antagonist.name if antagonist else "the adversary",
            "mentor": mentor.name if mentor else "the wise elder",
            "setting": setting or "a distant land",
            "dominant_trait": (protagonist.dominant_trait.name if protagonist and protagonist.dominant_trait else "determination"),
            "conflict": "a great challenge",
            "danger": "their own excess",
            "quest_goal": "a legendary prize",
            "moral": moral or "the truth reveals itself",
        }

        points: List[PlotPoint] = []
        for stage, desc_template in arc:
            desc = desc_template.format(**substitutions)
            involved: List[str] = []
            if protagonist:
                involved.append(protagonist.name)
            if stage in (PlotStage.CLIMAX, PlotStage.RISING_ACTION) and antagonist:
                involved.append(antagonist.name)
            points.append(PlotPoint(stage=stage, description=desc, characters_involved=involved))

        return points

    def generate_fable(
        self,
        template_id: str,
        characters: List[Character],
        setting: str = "",
        moral: str = "",
        title: str = "",
        archetype: str = "",
        holonomy_pattern: str = "",
        maps_to: str = "",
    ) -> Fable:
        """Generate a complete Fable from template, characters, and moral."""
        outline = self.generate_outline(template_id, characters, setting, moral)
        plot = "\n\n".join(f"[{p.stage.value}] {p.description}" for p in outline)

        tmpl = self.templates.get(template_id, {})
        style = tmpl.get("style", "classic")

        if not title:
            char_name = characters[0].name if characters else "The Wanderer"
            title = f"The {char_name} and the {style.title()} Truth"

        return Fable(
            title=title,
            characters=characters,
            setting=setting,
            plot=plot,
            moral=moral,
            style=style,
            archetype=archetype,
            holonomy_pattern=holonomy_pattern,
            maps_to=maps_to,
        )

    def generate_from_problem(
        self,
        problem: str,
        archetype: str = "",
        moral: str = "",
        count: int = 1,
    ) -> List[Fable]:
        """Generate fables inspired by a problem description."""
        from .moral import MoralEngine

        engine = MoralEngine()
        matches = engine.extract_morals(problem, top_n=count)

        fables: List[Fable] = []
        for match in matches:
            char = Character(
                name=f"Figure of {match.theme.replace('_', ' ').title()}",
                archetype=Archetype.TRICKSTER if "trick" in match.theme else Archetype.HERO,
                role="protagonist",
            )
            fable = self.generate_fable(
                template_id="classic_fable",
                characters=[char],
                setting="a realm of abstract forces",
                moral=match.moral,
                archetype=match.archetype,
            )
            fables.append(fable)

        return fables
