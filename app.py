"""Synthesis check: the thing a scientist opens.

    streamlit run app.py

Deliberately one screen: paste a sequence, get a verdict, get the reason in
the same units the scientist already argues in. The interface is not the
project; it exists so somebody who is not me can disagree with the model.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from synthesis_check.features import clean
from synthesis_check.model import MIN_LENGTH, check, fit, load_orders

st.set_page_config(page_title="Synthesis check", page_icon="·", layout="centered")


@st.cache_resource
def load():
    """Fit once per process. It takes a moment, and the room should not watch it twice."""
    orders = load_orders()
    return fit(orders), orders


model, orders = load()

st.markdown("#### Synthesis check")
st.caption("internal · nothing here leaves the building")

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

verdict = check(model, sequence)
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
