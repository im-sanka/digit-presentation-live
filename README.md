# Synthesis check

Live: **[digit-presentation-live.streamlit.app](https://digit-presentation-live.streamlit.app/)**

Will a vendor manage to build this DNA construct? Paste a sequence, get a
verdict, get the reason in units a scientist already argues in.

Twelve features read off the sequence, a logistic regression, leave-one-out
accuracy of 0.886 on 44 orders. The point is not that it is impressive. It is
that it is small, and that somebody who is not the author can now use it.

**The data is synthetic.** The real file is customer constructs under NDA.
`scripts/make_data.py` builds a stand-in with the same shape and the same
failure modes.

## Run it

```bash
pip install -r requirements.txt
streamlit run frontend/app.py
```

Then paste a sequence, or press one of the three example buttons.

The model is a backend on its own, and the Streamlit screen is only one of the
things that can ask it:

```bash
uvicorn synthesis_check.api:app                            # HTTP, :8000
python -m synthesis_check.mcp_server                       # MCP over stdio
claude mcp add synthesis-check -- python -m synthesis_check.mcp_server
```

See [docs/MCP.md](docs/MCP.md) for wiring it into Claude or any other assistant.

## Check it

```bash
python3 -m pytest -q          # the numbers that must not change, and the app driven headless
python3 -m scripts.fit        # prints the accuracy and the top weights
```

Expected:

```
44 orders, 20 of them failed
leave-one-out accuracy   0.886
always guessing the more common answer   0.545

what it is actually using
  hairpin_stem           +1.022  towards failure
  longest_repeat         +0.679  towards failure
  homopolymer_max        +0.648  towards failure
```

## Layout

```
backend/synthesis_check/  the model, installed as a package
  features/               twelve numbers from a sequence
  model.py                fit, score, check
  api.py                  HTTP front
  mcp_server.py           MCP front, for AI assistants
frontend/app.py           the Streamlit screen, asks the backend
scripts/                  make_data, fit, preload
tests/                    features, model, API, MCP, app
docs/                     ARCHITECTURE.md, DEVELOPING.md, MCP.md, DEPLOY.md
data/orders.csv           44 orders, 20 failed
notebook.ipynb            the analysis as it used to be handed over
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for how the pieces fit and
[docs/DEVELOPING.md](docs/DEVELOPING.md) for how to change them.


## Ship it

Push to `main` and Streamlit Community Cloud redeploys the live app. Steps for
the first time, and how to check it, are in [docs/DEPLOY.md](docs/DEPLOY.md).

Anywhere else:

```bash
docker compose up            # backend API :8000, MCP :8080, frontend :8501
docker compose up api mcp    # just the backend, for pipelines and assistants
```

In compose the frontend talks to the backend over HTTP. On a laptop or on
Streamlit Community Cloud it imports the backend and runs it in-process.

`.gitlab-ci.yml` runs the tests on every push, builds the image on `main`, and
then checks the live app answers.
The theme is in `.streamlit/config.toml`, the favicon in `frontend/static/`. The
conventions behind all three are written down in
`.claude/skills/ops-conventions/SKILL.md`, so the next project gets them for
free.
