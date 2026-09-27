"""The model as an MCP server, so any AI assistant can call it as a tool.

    python -m synthesis_check.mcp_server           # stdio, for Claude Code / Claude Desktop
    python -m synthesis_check.mcp_server --http    # streamable HTTP on :8080/mcp, for remote clients

Same check() as the app and the API. The assistant gets the verdict, the risk,
and the reasons in the units a scientist argues in, and can carry the
conversation from there.
"""

from __future__ import annotations

import sys

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from .features import COLUMNS, clean
from .model import MIN_LENGTH, check, fit, load_orders

server = MCPServer(
    "synthesis-check",
    instructions="Call check_sequence with a DNA sequence before advising anyone to order it.",
)
_model = fit(load_orders())


@server.tool()
def check_sequence(sequence: str) -> dict:
    """Will a DNA synthesis vendor manage to build this construct?

    Pass the raw sequence (FASTA headers, whitespace and numbers are stripped).
    Returns risk (0-1), likely_to_fail, human-readable reasons such as
    "repeat of 36 bp", and the twelve features the verdict rests on.
    """
    seq = clean(sequence)
    if len(seq) < MIN_LENGTH:
        # ToolError reaches the assistant as a message it can act on, not a stack trace
        raise ToolError(f"need at least {MIN_LENGTH} bases of A, C, G and T, got {len(seq)}")
    return check(_model, seq)


@server.resource("synthesis-check://features")
def feature_list() -> str:
    """The twelve features, in the order the model sees them."""
    return "\n".join(COLUMNS)


if __name__ == "__main__":
    if "--http" in sys.argv:
        server.run(transport="streamable-http", host="0.0.0.0", port=8080)
    else:
        server.run()
