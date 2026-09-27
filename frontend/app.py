"""Synthesis check: the thing a scientist opens.

    streamlit run frontend/app.py

Deliberately one screen: paste a sequence, get a verdict, get the reason in
the same units the scientist already argues in. The interface is not the
project; it exists so somebody who is not me can disagree with the model.

The frontend owns no model. With BACKEND_URL set it asks the API; without it
(Streamlit Community Cloud, a laptop) it imports the backend and runs it in
the same process. Either way the verdict comes from one check() function.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from synthesis_check.features import clean
from synthesis_check.model import MIN_LENGTH, load_orders

BACKEND_URL = os.environ.get("BACKEND_URL", "").rstrip("/")

st.set_page_config(
    page_title="Synthesis check",
    page_icon=str(Path(__file__).parent / "static" / "favicon.png"),
    layout="centered",
)


@st.cache_resource
def backend():
    """One callable that turns a sequence into a verdict, however it is wired."""
    if BACKEND_URL:
        def over_http(sequence: str) -> dict:
            r = requests.post(f"{BACKEND_URL}/check", json={"sequence": sequence}, timeout=10)
            r.raise_for_status()
            return r.json()
        return over_http

    # ponytail: in-process fallback so the Cloud deploy needs no second service
    from synthesis_check.model import check, fit
    model = fit(load_orders())
    return lambda sequence: check(model, sequence)


verdict_for = backend()
orders = load_orders()

st.markdown("#### Synthesis check")
st.caption("internal · nothing here leaves the building" + (f"  ·  backend {BACKEND_URL}" if BACKEND_URL else ""))

examples = {
    "a real gene fragment": orders.loc[orders.synthesised == "yes", "sequence"].iloc[0],
    "a tandem repeat": orders.loc[orders.synthesised == "no", "sequence"].iloc[0],
    "a GC-rich block": orders.loc[orders.synthesised == "no", "sequence"].iloc[1],
}

if "seq" not in st.session_state:
    st.session_state.seq = examples["a real gene fragment"]

for column, (label, seq) in zip(st.columns(len(examples)), examples.items()):
    if column.button(label, use_container_width=True):
        st.session_state.seq = seq

sequence = clean(st.text_area("Paste a sequence", key="seq", height=120))

if len(sequence) < MIN_LENGTH:
    st.info(f"Paste at least {MIN_LENGTH} bases of A, C, G and T.")
    st.stop()

verdict = verdict_for(sequence)
row = verdict["features"]

if verdict["likely_to_fail"]:
    st.error(f"**Likely to fail**  ·  {verdict['risk']:.0%} confidence")
else:
    st.success(f"**Should be fine**  ·  {1 - verdict['risk']:.0%} confidence")

st.caption(
    f"longest repeat {row['longest_repeat']} bp  ·  GC {row['gc_content']:.0f}%  ·  "
    f"worst window {row['max_window_gc']:.0f}%  ·  {row['length']} bp"
)

if verdict["reasons"]:
    st.write("**Flagged on:** " + ", ".join(verdict["reasons"]))
else:
    st.write("**Nothing over threshold.** No single feature is unusual.")

with st.expander("All twelve features"):
    st.dataframe(pd.DataFrame([row]).T.rename(columns={0: "value"}), use_container_width=True)

st.divider()
st.caption(
    "Wrong? Say so, and it becomes the next row of the training file, "
    f"which today is {len(orders)} orders."
)
