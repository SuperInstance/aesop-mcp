"""Tests for aesop_mcp."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from typing import Any, Dict

import pytest

# ---------------------------------------------------------------------------
# character.py
# ---------------------------------------------------------------------------
from aesop_mcp.character import Archetype, Character, Trait, _ARCHETYPE_TRAITS


class TestTrait:
    def test_valid_intensity(self) -> None:
        t = Trait("cunning", 9)
        assert t.name == "cunning"
        assert t.intensity == 9

    def test_invalid_intensity(self) -> None:
        with pytest.raises(ValueError):
            Trait("cunning", 11)
        with pytest.raises(ValueError):
            Trait("cunning", -1)


class TestCharacter:
    def test_default_traits_from_archetype(self) -> None:
        c = Character(name="Fox", archetype=Archetype.TRICKSTER)
        assert len(c.traits) > 0
        assert any(t.name == "cunning" for t in c.traits)

    def test_custom_traits(self) -> None:
        t = Trait("bravery", 8)
        c = Character(name="Lion", archetype=Archetype.HERO, traits=[t])
        assert len(c.traits) == 1
        assert c.traits[0].name == "bravery"

    def test_dominant_trait(self) -> None:
        c = Character(name="Owl", archetype=Archetype.SAGE)
        dt = c.dominant_trait
        assert dt is not None
        assert dt.intensity == max(t.intensity for t in c.traits)

    def test_weakness(self) -> None:
        c = Character(name="Donkey", archetype=Archetype.FOOL)
        w = c.weakness
        assert w is not None
        assert w.intensity == min(t.intensity for t in c.traits)

    def test_conflicts_with(self) -> None:
        trickster = Character(name="Fox", archetype=Archetype.TRICKSTER)
        hero = Character(name="Knight", archetype=Archetype.HERO)
        # trickster dominant = cunning, hero dominant = courage — not direct opposites
        # but let's test the mechanism
        assert isinstance(trickster.conflicts_with(hero), bool)

    def test_to_dict(self) -> None:
        c = Character(name="Fox", archetype=Archetype.TRICKSTER, role="protagonist")
        d = c.to_dict()
        assert d["name"] == "Fox"
        assert d["archetype"] == "trickster"
        assert "traits" in d

    def test_all_archetypes_have_defaults(self) -> None:
        for arch in Archetype:
            c = Character(name="Test", archetype=arch)
            assert len(c.traits) > 0, f"No default traits for {arch}"


# ---------------------------------------------------------------------------
# fable.py
# ---------------------------------------------------------------------------
from aesop_mcp.fable import Fable


class TestFable:
    def test_basic_fable(self) -> None:
        f = Fable(title="The Fox and the Grapes", moral="It's easy to despise what you cannot have.")
        assert f.style == "classic"
        assert f.moral

    def test_summary(self) -> None:
        fox = Character(name="Fox", archetype=Archetype.TRICKSTER)
        f = Fable(
            title="Test Fable",
            characters=[fox],
            setting="A vineyard",
            plot="A fox tried to reach grapes.",
            moral="Sour grapes.",
        )
        s = f.summary
        assert "Test Fable" in s
        assert "Fox" in s
        assert "Sour grapes" in s

    def test_to_dict(self) -> None:
        f = Fable(title="Test", moral="Be good.")
        d = f.to_dict()
        assert d["title"] == "Test"
        assert d["moral"] == "Be good."

    def test_from_dict(self) -> None:
        data = {
            "title": "The Tortoise and the Hare",
            "characters": [{"name": "Tortoise", "archetype": "hero", "role": "protagonist"}],
            "moral": "Slow and steady wins the race.",
        }
        f = Fable.from_dict(data)
        assert f.title == "The Tortoise and the Hare"
        assert len(f.characters) == 1
        assert f.characters[0].name == "Tortoise"

    def test_from_dict_unknown_archetype(self) -> None:
        data = {"title": "Test", "characters": [{"name": "X", "archetype": "unknown_thing"}]}
        f = Fable.from_dict(data)
        assert f.characters[0].archetype == Archetype.HERO  # fallback


# ---------------------------------------------------------------------------
# moral.py
# ---------------------------------------------------------------------------
from aesop_mcp.moral import MoralEngine, MoralMatch, MORAL_TEMPLATES


class TestMoralEngine:
    def test_extract_morals_hubris(self) -> None:
        engine = MoralEngine()
        results = engine.extract_morals("The overconfident king flew too high and fell.")
        assert len(results) > 0
        assert results[0].theme == "hubris"

    def test_extract_morals_empty(self) -> None:
        engine = MoralEngine()
        results = engine.extract_morals("A completely unrelated text about weather.")
        # May or may not match; just ensure no crash
        assert isinstance(results, list)

    def test_find_moral(self) -> None:
        engine = MoralEngine()
        m = engine.find_moral("A system that repeats the same cycle endlessly.")
        assert m is not None
        assert m.theme == "perseverance"

    def test_compare_morals(self) -> None:
        engine = MoralEngine()
        sim = engine.compare_morals(
            "More constraints make a brittle system.",
            "Constraints make systems brittle.",
        )
        assert 0 < sim < 1

    def test_compare_identical(self) -> None:
        engine = MoralEngine()
        sim = engine.compare_morals("Slow and steady wins.", "Slow and steady wins.")
        assert sim == 1.0

    def test_converge(self) -> None:
        engine = MoralEngine()
        morals = [
            "More constraints make a brittle system.",
            "Too many constraints create brittleness.",
            "The quick brown fox jumps over the lazy dog.",
        ]
        clusters = engine.converge(morals, threshold=0.1)
        assert len(clusters) >= 1

    def test_negative_space(self) -> None:
        engine = MoralEngine()
        result = engine.negative_space(
            "The echo chamber feedback loop creates isolation and conformity",
            ["Self-consistency is not consensus."],
        )
        assert "uncovered_terms" in result
        assert "coverage" in result

    def test_extract_moral_sentences(self) -> None:
        engine = MoralEngine()
        text = "The story teaches us that hubris leads to ruin. The moral of the story is: be humble."
        sentences = engine.extract_moral_sentences(text)
        assert len(sentences) >= 1

    def test_top_n_limits(self) -> None:
        engine = MoralEngine()
        results = engine.extract_morals("overconfident pride hubris cycle repeat stuck", top_n=2)
        assert len(results) <= 2


# ---------------------------------------------------------------------------
# narrative.py
# ---------------------------------------------------------------------------
from aesop_mcp.narrative import NarrativeEngine, PlotStage, STORY_TEMPLATES, PLOT_ARCS


class TestNarrativeEngine:
    def test_list_templates(self) -> None:
        engine = NarrativeEngine()
        templates = engine.list_templates()
        assert len(templates) > 0
        assert any(t["id"] == "classic_fable" for t in templates)

    def test_generate_outline(self) -> None:
        engine = NarrativeEngine()
        fox = Character(name="Fox", archetype=Archetype.TRICKSTER)
        outline = engine.generate_outline(
            "classic_fable",
            characters=[fox],
            setting="A forest",
            moral="Cleverness beats strength.",
        )
        assert len(outline) > 0
        assert outline[0].stage == PlotStage.EXPOSITION
        assert "Fox" in outline[0].description

    def test_generate_outline_unknown_template(self) -> None:
        engine = NarrativeEngine()
        with pytest.raises(ValueError, match="Unknown template"):
            engine.generate_outline("nonexistent", [])

    def test_generate_fable(self) -> None:
        engine = NarrativeEngine()
        fox = Character(name="Fox", archetype=Archetype.TRICKSTER)
        fable = engine.generate_fable(
            "trickster_tale",
            characters=[fox],
            setting="A barnyard",
            moral="Brain beats brawn.",
        )
        assert isinstance(fable, Fable)
        assert "Fox" in fable.plot
        assert fable.moral == "Brain beats brawn."

    def test_generate_from_problem(self) -> None:
        engine = NarrativeEngine()
        fables = engine.generate_from_problem(
            "An overconfident system that adds too many constraints and melts down.",
            count=3,
        )
        assert len(fables) > 0
        assert all(isinstance(f, Fable) for f in fables)


# ---------------------------------------------------------------------------
# server.py
# ---------------------------------------------------------------------------
from aesop_mcp.server import MCPServer, TOOL_DEFINITIONS


class TestMCPServer:
    def test_list_tools(self) -> None:
        server = MCPServer()
        tools = server.list_tools()
        assert len(tools) == 5
        names = {t["name"] for t in tools}
        assert names == {
            "generate_fable",
            "analyze_morals",
            "fable_set",
            "list_archetypes",
            "list_templates",
        }

    def test_call_unknown_tool(self) -> None:
        server = MCPServer()
        result = server.call_tool("nonexistent", {})
        assert "error" in result

    def test_generate_fable_tool(self) -> None:
        server = MCPServer()
        result = server.call_tool("generate_fable", {
            "template_id": "classic_fable",
            "protagonist_name": "Raven",
            "protagonist_archetype": "trickster",
            "setting": "A tower",
            "moral": "Don't trust flatterers.",
        })
        assert "fable" in result
        assert result["fable"]["moral"] == "Don't trust flatterers."

    def test_analyze_morals_tool(self) -> None:
        server = MCPServer()
        result = server.call_tool("analyze_morals", {
            "text": "An echo chamber of self-reinforcing feedback loops",
        })
        assert "morals" in result
        assert "negative_space" in result

    def test_fable_set_tool(self) -> None:
        server = MCPServer()
        result = server.call_tool("fable_set", {
            "problem": "A distributed consensus system with echo chambers and forced conformity",
            "count": 5,
        })
        assert "fables" in result
        assert "convergence" in result
        assert "negative_space" in result
        assert result["count"] <= 5

    def test_list_archetypes_tool(self) -> None:
        server = MCPServer()
        result = server.call_tool("list_archetypes", {})
        assert "archetypes" in result
        assert "trickster" in result["archetypes"]
        assert "hero" in result["archetypes"]

    def test_list_templates_tool(self) -> None:
        server = MCPServer()
        result = server.call_tool("list_templates", {})
        assert "templates" in result
        assert len(result["templates"]) > 0

    def test_tool_schemas_valid(self) -> None:
        for tool in TOOL_DEFINITIONS:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            schema = tool["inputSchema"]
            assert schema["type"] == "object"
            assert "properties" in schema


# ---------------------------------------------------------------------------
# Integration: HTTP server smoke test
# ---------------------------------------------------------------------------
class TestHTTPIntegration:
    @pytest.fixture(scope="class")
    def http_server(self) -> Any:
        """Start the HTTP server in a subprocess, yield the base URL, then kill it."""
        import threading

        port = 14041
        proc = subprocess.Popen(
            [sys.executable, "-m", "aesop_mcp"],
            env={**os.environ, "AESOP_PORT": str(port)},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/tmp/aesop-mcp",
        )
        # Give the server time to start
        time.sleep(1.5)
        yield f"http://127.0.0.1:{port}"
        proc.terminate()
        proc.wait(timeout=5)

    def _get(self, base: str, path: str) -> Dict[str, Any]:
        resp = urllib.request.urlopen(f"{base}{path}")
        return json.loads(resp.read())

    def _post(self, base: str, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps(data).encode()
        req = urllib.request.Request(
            f"{base}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())

    def test_root(self, http_server: str) -> None:
        data = self._get(http_server, "/")
        assert data["service"] == "🏛️ Aesop-MCP"

    def test_fable_endpoint(self, http_server: str) -> None:
        data = self._get(http_server, "/fable?problem=hubris+and+overconfidence")
        assert "fables" in data

    def test_archetypes_endpoint(self, http_server: str) -> None:
        data = self._get(http_server, "/archetypes")
        assert "archetypes" in data

    def test_templates_endpoint(self, http_server: str) -> None:
        data = self._get(http_server, "/templates")
        assert "templates" in data

    def test_tools_call(self, http_server: str) -> None:
        data = self._post(http_server, "/tools/call", {
            "name": "generate_fable",
            "arguments": {"template_id": "quest", "protagonist_name": "Odysseus"},
        })
        assert "fable" in data
