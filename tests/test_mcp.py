"""The MCP tool is the same check(), reachable by any assistant."""

import asyncio

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from synthesis_check.mcp_server import check_sequence, server

NASTY = "GGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCC"


def test_tool_is_registered():
    tools = asyncio.run(server.list_tools())
    assert [t.name for t in tools] == ["check_sequence"]
    assert "vendor" in tools[0].description.lower()


def test_tool_gives_the_verdict():
    result = check_sequence(NASTY)
    assert result["likely_to_fail"] is True
    assert any("repeat" in r for r in result["reasons"])


def test_tool_rejects_short_input():
    with pytest.raises(ToolError):
        check_sequence(">header\nACGT")
