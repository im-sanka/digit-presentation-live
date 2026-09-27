"""The HTTP API: the same model, without a browser in front of it.

The Streamlit frontend calls this when BACKEND_URL is set, and so can a
pipeline, a LIMS, or anything else that speaks JSON.

    pip install -e .[api]
    uvicorn synthesis_check.api:app --reload

    curl -X POST localhost:8000/check -H 'content-type: application/json' \\
         -d '{"sequence": "GGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCC"}'
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .features import clean
from .model import MIN_LENGTH, check, fit, load_orders

app = FastAPI(title="Synthesis check", version="1.0")
model = fit(load_orders())


class Order(BaseModel):
    sequence: str


@app.post("/check")
def check_order(order: Order) -> dict:
    sequence = clean(order.sequence)
    if len(sequence) < MIN_LENGTH:
        raise HTTPException(422, f"need at least {MIN_LENGTH} bases of A, C, G and T")
    return check(model, sequence)


@app.get("/health")
def health() -> dict:
    return {"ok": True}
