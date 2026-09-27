# Developing

```bash
pip install -r requirements.txt

python3 -m pytest -q             # the numbers that must not change
python3 -m scripts.fit           # 44 orders, LOO accuracy, top weights
python3 -m scripts.make_data     # rebuild data/orders.csv from a fixed seed
streamlit run frontend/app.py    # the frontend, on localhost:8501
uvicorn synthesis_check.api:app  # the backend API, on localhost:8000
python -m synthesis_check.mcp_server   # the backend as an MCP server, stdio
python3 -i -m scripts.preload    # the warm REPL for typing the four lines
```

Adding a feature:

1. Write the function in `backend/synthesis_check/features/sequence.py` or `structure.py`.
2. Add it to `featurise` and to `COLUMNS` in `backend/synthesis_check/features/__init__.py`.
3. If a scientist could argue with a threshold on it, add a rule to `model.FLAGS`.
4. Run the tests. The accuracy assertion will tell you if it changed the model.
