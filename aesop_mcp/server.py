"""MCPServer — Model Context Protocol server for fable generation and moral analysis."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from .character import Archetype, Character
from .fable import Fable
from .moral import MORAL_TEMPLATES, MoralEngine
from .narrative import NarrativeEngine


# Tool definitions for MCP
TOOL_DEFINITIONS = [
    {
        "name": "generate_fable",
        "description": (
            "Generate a fable from characters, a plot template, and a moral. "
            "Returns a structured fable with narrative arc."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "template_id": {
                    "type": "string",
                    "description": "Plot template: classic_fable, cautionary_tale, quest, trickster_tale",
                },
                "protagonist_name": {"type": "string", "description": "Name of the main character"},
                "protagonist_archetype": {
                    "type": "string",
                    "description": "Archetype: trickster, sage, fool, hero, outcast, creator, ruler, caregiver, explorer, rebel",
                },
                "setting": {"type": "string", "description": "Where the story takes place"},
                "moral": {"type": "string", "description": "The moral lesson of the fable"},
                "title": {"type": "string", "description": "Optional title for the fable"},
            },
            "required": ["template_id"],
        },
    },
    {
        "name": "analyze_morals",
        "description": "Extract and rank morals from a text or problem description.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze for moral themes"},
                "top_n": {"type": "integer", "description": "Number of morals to return (default 5)"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "fable_set",
        "description": (
            "Generate multiple fables for a problem, then compute convergence "
            "and negative space — where the truth lives in the overlap and the gap."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "problem": {"type": "string", "description": "The problem or situation to explore"},
                "count": {"type": "integer", "description": "Number of fables (default 8)"},
            },
            "required": ["problem"],
        },
    },
    {
        "name": "list_archetypes",
        "description": "List available character archetypes and their trait profiles.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_templates",
        "description": "List available narrative plot templates.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


class MCPServer:
    """MCP-compatible server exposing fable generation and moral analysis tools."""

    def __init__(self) -> None:
        self.moral_engine = MoralEngine()
        self.narrative_engine = NarrativeEngine()

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return MCP tool definitions."""
        return TOOL_DEFINITIONS

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch a tool call by name with the given arguments."""
        handlers = {
            "generate_fable": self._tool_generate_fable,
            "analyze_morals": self._tool_analyze_morals,
            "fable_set": self._tool_fable_set,
            "list_archetypes": self._tool_list_archetypes,
            "list_templates": self._tool_list_templates,
        }
        handler = handlers.get(name)
        if handler is None:
            return {"error": f"Unknown tool: {name}"}
        return handler(arguments)

    # -- Tool handlers --

    def _tool_generate_fable(self, args: Dict[str, Any]) -> Dict[str, Any]:
        template_id = args.get("template_id", "classic_fable")
        archetype_str = args.get("protagonist_archetype", "hero")
        try:
            archetype = Archetype(archetype_str)
        except ValueError:
            archetype = Archetype.HERO

        character = Character(
            name=args.get("protagonist_name", "Hero"),
            archetype=archetype,
            role="protagonist",
        )
        fable = self.narrative_engine.generate_fable(
            template_id=template_id,
            characters=[character],
            setting=args.get("setting", ""),
            moral=args.get("moral", ""),
            title=args.get("title", ""),
        )
        return {"fable": fable.to_dict()}

    def _tool_analyze_morals(self, args: Dict[str, Any]) -> Dict[str, Any]:
        text = args.get("text", "")
        top_n = args.get("top_n", 5)
        matches = self.moral_engine.extract_morals(text, top_n=top_n)
        neg = self.moral_engine.negative_space(text, [m.moral for m in matches])
        return {
            "morals": [
                {
                    "theme": m.theme,
                    "moral": m.moral,
                    "archetype": m.archetype,
                    "relevance": m.relevance,
                    "matched_keywords": m.matched_keywords,
                }
                for m in matches
            ],
            "negative_space": neg,
        }

    def _tool_fable_set(self, args: Dict[str, Any]) -> Dict[str, Any]:
        problem = args.get("problem", "")
        count = args.get("count", 8)
        matches = self.moral_engine.extract_morals(problem, top_n=count)

        fables_out: List[Dict[str, Any]] = []
        for match in matches:
            char = Character(
                name=f"Spirit of {match.theme.replace('_', ' ').title()}",
                archetype=Archetype.HERO,
                role="protagonist",
            )
            fable = self.narrative_engine.generate_fable(
                template_id="classic_fable",
                characters=[char],
                setting="a realm of abstract forces",
                moral=match.moral,
                archetype=match.archetype,
            )
            fables_out.append(fable.to_dict())

        # Convergence
        morals_list = [m.moral for m in matches]
        clusters = self.moral_engine.converge(morals_list)
        neg = self.moral_engine.negative_space(problem, morals_list)

        return {
            "problem": problem,
            "fables": fables_out,
            "count": len(fables_out),
            "convergence": {
                "clusters": clusters,
                "consensus_count": len(clusters),
            },
            "negative_space": neg,
        }

    def _tool_list_archetypes(self, _args: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for arch in Archetype:
            char = Character(name="Sample", archetype=arch)
            result[arch.value] = {
                "traits": [{"name": t.name, "intensity": t.intensity} for t in char.traits],
                "dominant_trait": char.dominant_trait.name if char.dominant_trait else None,
            }
        return {"archetypes": result}

    def _tool_list_templates(self, _args: Dict[str, Any]) -> Dict[str, Any]:
        return {"templates": self.narrative_engine.list_templates()}

    # -- HTTP interface for backward compatibility --

    def run_http(self, port: Optional[int] = None) -> None:
        """Run an HTTP server (backward compat with the original single-file version)."""
        import http.server
        from http.server import HTTPServer, BaseHTTPRequestHandler

        p = port or int(os.environ.get("AESOP_PORT", "4041"))
        server_ref = self

        class Handler(BaseHTTPRequestHandler):
            def _json(self, data: Any, code: int = 200) -> None:
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(data, indent=2).encode())

            def _body(self) -> Dict[str, Any]:
                try:
                    length = int(self.headers.get("Content-Length", 0))
                    if length > 0:
                        raw = self.rfile.read(length)
                        return json.loads(raw)
                except Exception:
                    pass
                return {}

            def do_OPTIONS(self) -> None:
                self.send_response(204)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()

            def do_GET(self) -> None:
                path = self.path.split("?")[0]
                params: Dict[str, str] = {}
                if "?" in self.path:
                    qs = self.path.split("?", 1)[1]
                    for part in qs.split("&"):
                        if "=" in part:
                            k, v = part.split("=", 1)
                            params[k] = v.replace("+", " ")

                if path == "/":
                    self._json({
                        "service": "🏛️ Aesop-MCP",
                        "version": "0.2.0",
                        "tools": [t["name"] for t in TOOL_DEFINITIONS],
                        "endpoints": {
                            "GET /": "This help",
                            "GET /fable?problem=X&count=N": "Fable set for a problem",
                            "GET /archetypes": "List archetypes",
                            "GET /templates": "List plot templates",
                            "GET /morals?text=X": "Analyze morals in text",
                            "POST /tools/call": "Call an MCP tool",
                        },
                    })
                elif path.startswith("/fable"):
                    self._json(server_ref.call_tool("fable_set", {
                        "problem": params.get("problem", "a general challenge"),
                        "count": int(params.get("count", "8")),
                    }))
                elif path == "/archetypes":
                    self._json(server_ref.call_tool("list_archetypes", {}))
                elif path == "/templates":
                    self._json(server_ref.call_tool("list_templates", {}))
                elif path.startswith("/morals"):
                    self._json(server_ref.call_tool("analyze_morals", {
                        "text": params.get("text", ""),
                    }))
                else:
                    self._json({"error": "not found"}, 404)

            def do_POST(self) -> None:
                body = self._body()
                if self.path == "/tools/call":
                    tool_name = body.get("name", "")
                    tool_args = body.get("arguments", {})
                    self._json(server_ref.call_tool(tool_name, tool_args))
                elif self.path == "/translate":
                    self._json(server_ref.call_tool("analyze_morals", {
                        "text": body.get("text", ""),
                    }))
                elif self.path == "/moral":
                    event_text = json.dumps(body.get("event", body))
                    self._json(server_ref.call_tool("analyze_morals", {
                        "text": event_text,
                    }))
                else:
                    self._json({"error": "not found"}, 404)

        print(f"🏛️ Aesop-MCP v0.2.0 — Fable Generation & Moral Analysis")
        print(f"   Port: {p}")
        print(f"   Tools: {', '.join(t['name'] for t in TOOL_DEFINITIONS)}")
        httpd = HTTPServer(("0.0.0.0", p), Handler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
            httpd.server_close()
