# Using the model from an AI assistant

The backend is an MCP server. Any assistant that speaks MCP can call
`check_sequence` and get the same verdict the app shows, with the reasons.

## Claude Code

From the repo root, with the package installed (`pip install -r requirements.txt`):

```bash
claude mcp add synthesis-check -- python -m synthesis_check.mcp_server
```

Then ask: *"Will this sequence synthesise? GGCGCCGGCGCC..."* and Claude calls the tool.

## Claude Desktop, Cursor, and other stdio clients

Add to the client's MCP config (for Claude Desktop, `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "synthesis-check": {
      "command": "python",
      "args": ["-m", "synthesis_check.mcp_server"],
      "cwd": "/path/to/digit-presentation-live"
    }
  }
}
```

## Remote clients over HTTP

```bash
docker compose up mcp                 # or: python -m synthesis_check.mcp_server --http
```

The server listens on `http://localhost:8080/mcp` (streamable HTTP). Point any
MCP client with an HTTP transport at that URL.

## What the assistant sees

| | |
| --- | --- |
| tool | `check_sequence(sequence: str) -> dict` |
| returns | `risk`, `likely_to_fail`, `reasons` (e.g. "repeat of 36 bp"), `features` (twelve numbers) |
| resource | `synthesis-check://features`, the twelve feature names in model order |
| rejects | fewer than 40 bases of A, C, G, T after cleaning |

## Not an assistant?

Same function over plain HTTP:

```bash
docker compose up api
curl -X POST localhost:8000/check -H 'content-type: application/json' \
     -d '{"sequence": "GGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCC"}'
```
