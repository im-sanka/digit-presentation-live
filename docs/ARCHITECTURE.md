# How it fits together

```
sequence  ──▶  synthesis_check.features  ──▶  twelve numbers
                                                   │
data/orders.csv  ──▶  synthesis_check.model  ──▶  LogisticRegression
                                                   │
                     app.py (Streamlit)  ◀──────────┤  check(model, sequence)
                     synthesis_check.api (FastAPI) ◀─┘
```

## Modules

| module | owns | imports |
| --- | --- | --- |
| `synthesis_check/features/sequence.py` | composition: GC, Tm, windows, reverse complement | nothing |
| `synthesis_check/features/structure.py` | repeats, hairpins, homopolymer and dinucleotide runs | `sequence` |
| `synthesis_check/features/__init__.py` | `COLUMNS`, `featurise`, `features`, `clean` | both above |
| `synthesis_check/model.py` | load, fit, leave-one-out score, `check` with reasons | `features` |
| `synthesis_check/api.py` | HTTP front on `check`, optional | `model` |
| `app.py` | Streamlit front on `check` | `model` |
| `scripts/` | `make_data`, `fit`, `preload`: run with `python3 -m scripts.<name>` | `model` |
| `tests/` | the numbers that must not change | everything |

## Rules that keep it small

- Features are pure functions of a string. No I/O, no globals, no state.
- The model is fit in exactly one place, `model.fit`. The app and the API call it; they do not own a classifier.
- Thresholds that produce human-readable reasons live in `model.FLAGS`, next to the model they explain.
- Paths resolve from the package, so every script works from any working directory.
- Anything that changes the number 0.886 fails `tests/test_model.py`.
