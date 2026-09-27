# Deploying

The app runs on Streamlit Community Cloud, straight from this repo. There is
no build step: the service installs `requirements.txt` (which installs the backend package) and runs `frontend/app.py`.

Live: https://digit-presentation-live.streamlit.app/

## First time

1. Sign in at https://share.streamlit.io with the GitHub account that owns the repo.
2. New app, pick this repo, branch `main`, main file `frontend/app.py`.
3. Advanced settings: Python 3.11. No secrets are needed; nothing here calls out.
4. Settings, Sharing: **Public**. A private app answers every request with a
   redirect to a login page, including the health check below.
5. Deploy. The first build takes a couple of minutes, every push after that redeploys on its own.

## Every time after

Push to `main`. That is the deploy.

## Check it

```bash
curl -sf https://digit-presentation-live.streamlit.app/_stcore/health   # prints: ok
python -m pytest -q tests/test_app.py                                    # the app, driven headless
```

The `smoke` stage in `.gitlab-ci.yml` runs the first of those after every
push to `main`, so a broken deploy fails the pipeline instead of the demo.

## Before a talk

Community Cloud sleeps when idle. Open the URL an hour before and again in the
last five minutes. Keep `streamlit run frontend/app.py` running locally as the backup.

## Elsewhere

Anything that runs a container: `docker compose up`, or pull the image the CI
pushed to the registry. Same app, same numbers.
