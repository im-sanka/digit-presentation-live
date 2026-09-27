# How it fits together

Two halves. The backend owns the features and the model and answers one
question: will this sequence come back failed? The frontend is one of several
things that ask.

```
                         backend/synthesis_check
                    ┌──────────────────────────────┐
sequence ──────────▶│ features   twelve numbers    │
data/orders.csv ───▶│ model      fit, score, check │
                    └──────────────┬───────────────┘
                                   │ check(model, sequence)
             ┌─────────────────────┼─────────────────────┐
             ▼                     ▼                     ▼
      api.py  (HTTP :8000)   mcp_server.py (:8080)   in-process import
             ▲                     ▲                     ▲
      frontend/app.py         Claude, any MCP        frontend/app.py
      curl, a LIMS,           client, another        on Streamlit Cloud,
      a pipeline              AI assistant           or a laptop
```

## Backend: `backend/synthesis_check/`

| module | owns | imports |
| --- | --- | --- |
| `features/sequence.py` | composition: GC, Tm, windows, reverse complement | nothing |
| `features/structure.py` | repeats, hairpins, homopolymer and dinucleotide runs | `sequence` |
| `features/__init__.py` | `COLUMNS`, `featurise`, `features`, `clean` | both above |
| `model.py` | load, fit, leave-one-out score, `check` with reasons | `features` |
| `api.py` | HTTP front on `check`: `POST /check`, `GET /health` | `model` |
| `mcp_server.py` | MCP front on `check`: tool `check_sequence`, resource `features` | `model` |

Installed as a package (`pip install -e .`, see `pyproject.toml`), so every
front imports `synthesis_check` the same way from anywhere.

## Frontend: `frontend/`

`app.py` is the Streamlit screen a scientist opens. It owns no model. With
`BACKEND_URL` set it posts to the API; without it, it imports the backend and
runs `check` in-process. Same function, same numbers.

## Around them

| path | what |
| --- | --- |
| `scripts/` | `make_data`, `fit`, `preload`: `python -m scripts.<name>` |
| `tests/` | features, model, API, MCP tool, and the app driven headless |
| `data/orders.csv` | 44 orders, 20 failed, synthetic |
| `Dockerfile`, `docker-compose.yml` | one image; `api`, `mcp` and `app` are three commands on it |

## Rules that keep it small

- Features are pure functions of a string. No I/O, no globals, no state.
- The model is fit in exactly one place, `model.fit`. Fronts call it; they do not own a classifier.
- Every front returns the dict from `model.check`, unchanged. A new front is a new file that calls `check`, nothing else.
- Thresholds that produce human-readable reasons live in `model.FLAGS`, next to the model they explain.
- Anything that changes the number 0.886 fails `tests/test_model.py`.
