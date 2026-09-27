---
name: ops-conventions
description: How this team ships a small Python app. Use when adding CI, containers, or Streamlit styling to a project in this repo.
---

# Ops conventions

## GitLab CI
- Two stages, `test` then `build`. Nothing else until somebody needs it.
- `test` runs on every push: `pip install -r requirements.txt`, `pytest -q`, and the one script that prints the headline number.
- `build` runs only on the default branch, builds the Dockerfile with docker-in-docker, tags with the short SHA and `latest`, pushes to the project registry.
- Cache pip under `.cache/pip`.

## Docker
- One `Dockerfile`, `python:3.11-slim`, copy only what the app imports.
- Add a `HEALTHCHECK` against `/_stcore/health` for Streamlit apps.
- `docker-compose.yml` lists one service per process, all built from the same image. Optional processes (an API) are separate services, not flags.

## Streamlit styling
- Theme lives in `.streamlit/config.toml`. Primary colour is the "fine" green `#5d8f7e`; the "failed" red is `#c2506a`. Same two colours as the plots.
- Favicon is `static/favicon.png`, passed as `page_icon`. Keep it 64px, one idea.
- `headless = true` and `gatherUsageStats = false` in the server section.

## Backend and frontend
- The model lives in `backend/<package>/`, installed with `pip install -e .` from a `pyproject.toml` at the root, so every front imports it the same way.
- Fronts are thin files that call one function: `api.py` for HTTP, `mcp_server.py` for AI assistants, `frontend/app.py` for people. A new front never owns a model.
- MCP servers use the official `mcp` SDK (`MCPServer`), stdio by default, `--http` for streamable HTTP on :8080. One tool, named for the question it answers.
- The frontend reads `BACKEND_URL`; set it in compose, leave it unset where a second service is not available.
