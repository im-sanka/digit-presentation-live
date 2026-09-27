# Synthesis check

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
streamlit run app.py
```

Then paste a sequence, or press one of the three example buttons.

## Check it

```bash
python3 -m pytest -q          # the numbers that must not change
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
synthesis_check/          the package
  features/               twelve numbers from a sequence
    sequence.py           composition: GC, Tm, windows
    structure.py          repeats, hairpins, runs
  model.py                fit, score, explain
  api.py                  optional HTTP front
app.py                    the Streamlit app
scripts/                  make_data, fit, preload
tests/                    pytest
docs/                     ARCHITECTURE.md, DEVELOPING.md
data/orders.csv           44 orders, 20 failed
notebook.ipynb            the analysis as it used to be handed over
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for how the pieces fit and
[docs/DEVELOPING.md](docs/DEVELOPING.md) for how to change them.

## The optional branch

Only if something other than a person is asking:

```bash
pip install fastapi uvicorn
uvicorn synthesis_check.api:app --reload
curl -X POST localhost:8000/check -H 'content-type: application/json' \
     -d '{"sequence": "GGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCC"}'
```
