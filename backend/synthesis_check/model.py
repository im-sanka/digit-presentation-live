"""Fit the classifier, score it, and explain a verdict.

One place for the model so the app, the API and the scripts cannot drift
apart. Leave-one-out rather than a held-out split, because a 20% test set of
44 rows is nine sequences and the score would swing ten points depending on
which nine.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut, cross_val_score

from .features import COLUMNS, featurise, features

#: the training file, resolved from the package so scripts work from any cwd
# ponytail: the file lives at the repo root so the notebook on branch 1 and the
# scripts keep working; point ORDERS_CSV at it when the layout differs
DATA = Path(os.environ.get("ORDERS_CSV", Path(__file__).resolve().parents[2] / "data" / "orders.csv"))

#: fewer bases than this and the windows are meaningless
MIN_LENGTH = 40

# Thresholds a scientist can argue with, rather than a number they cannot.
# GC is the only feature where both ends are a problem, so it gets one rule
# pointing each way.
FLAGS = [
    ("longest_repeat", lambda v: v >= 10, lambda v: f"repeat of {int(v)} bp"),
    ("max_window_gc", lambda v: v >= 75, lambda v: f"a 50 bp window at {v:.0f}% GC"),
    ("min_window_gc", lambda v: v <= 25, lambda v: f"a 50 bp window at only {v:.0f}% GC"),
    ("homopolymer_max", lambda v: v >= 8, lambda v: f"{int(v)} of the same base in a row"),
    ("dinucleotide_repeat", lambda v: v >= 20, lambda v: f"a {int(v)} bp dinucleotide tract"),
    ("hairpin_stem", lambda v: v >= 12, lambda v: f"a {int(v)} bp hairpin stem"),
]


def load_orders(path: Path = DATA) -> pd.DataFrame:
    return pd.read_csv(path)


def split(orders: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """The order file in, X and y out. `y` is True when the order failed."""
    return features(orders.sequence), orders.synthesised == "no"


def loo_accuracy(orders: pd.DataFrame) -> float:
    X, y = split(orders)
    return cross_val_score(LogisticRegression(max_iter=1000), X, y, cv=LeaveOneOut()).mean()


def fit(orders: pd.DataFrame) -> LogisticRegression:
    X, y = split(orders)
    return LogisticRegression(max_iter=1000).fit(X, y)


def weights(model: LogisticRegression) -> pd.Series:
    """Coefficients by size, so the top of the list is what the model leans on."""
    return pd.Series(model.coef_[0], index=COLUMNS).sort_values(key=abs, ascending=False)


def check(model: LogisticRegression, sequence: str) -> dict:
    """One sequence in, a verdict with reasons out.

    The reasons are in units a scientist already argues in, which is what makes
    disagreement possible, and a disagreement is the next row of the training file.
    """
    row = featurise(sequence)
    risk = float(model.predict_proba(pd.DataFrame([row], columns=COLUMNS))[0][1])
    reasons = [render(row[name]) for name, over, render in FLAGS if over(row[name])]
    return {
        "risk": round(risk, 3),
        "likely_to_fail": risk >= 0.5,
        "reasons": reasons,
        "features": row,
    }
