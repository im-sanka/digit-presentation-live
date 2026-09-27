"""The warm REPL you build in front of the room.

    python3 -i -m scripts.preload

Everything slow or boring has already happened: imports done, file read,
`features` imported. What is left is the four lines that are actually the
model, and you type those while people watch.
"""

from __future__ import annotations

import pandas as pd  # noqa: F401  (in scope for the REPL)
from sklearn.linear_model import LogisticRegression  # noqa: F401
from sklearn.model_selection import LeaveOneOut, cross_val_score  # noqa: F401

from synthesis_check.features import features  # noqa: F401
from synthesis_check.model import load_orders

df = load_orders()

print(f"\n  {len(df)} orders, three columns: {', '.join(df.columns)}")
print("  ready: pandas, sklearn and features are loaded\n")
print("  type:")
print("      X = features(df.sequence)")
print("      y = df.synthesised == 'no'")
print("      clf = LogisticRegression(max_iter=1000)")
print("      cross_val_score(clf, X, y, cv=LeaveOneOut()).mean()\n")
