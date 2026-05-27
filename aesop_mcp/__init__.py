"""
Aesop-MCP — A Model Context Protocol server for fable generation and moral reasoning.

One fable is a sample. Ten fables are a measurement of the space.
The truth is where they converge. The negative space between them
is what none capture alone — and that is often the most interesting part.
"""

from .character import Character, Archetype
from .fable import Fable
from .moral import MoralEngine
from .narrative import NarrativeEngine
from .server import MCPServer

__version__ = "0.2.0"
__all__ = [
    "Character",
    "Archetype",
    "Fable",
    "MoralEngine",
    "NarrativeEngine",
    "MCPServer",
]
