"""Allow running `python -m aesop_mcp` or `python -m aesop_mcp.server`."""
from .server import MCPServer

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else None
    MCPServer().run_http(port)
