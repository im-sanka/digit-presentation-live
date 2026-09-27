"""Fit the classifier and say how well it does.

    python3 -m scripts.fit

The reference copy of the four lines you type on stage, complete and runnable
if the live typing goes wrong.
"""

from __future__ import annotations

from synthesis_check.model import fit, load_orders, loo_accuracy, weights

orders = load_orders()
failed = orders.synthesised == "no"

print(f"{len(orders)} orders, {int(failed.sum())} of them failed")
print(f"leave-one-out accuracy   {loo_accuracy(orders):.3f}")
print(f"always guessing the more common answer   {max(failed.mean(), 1 - failed.mean()):.3f}")

print("\nwhat it is actually using")
for name, weight in weights(fit(orders)).head(5).items():
    direction = "towards failure" if weight > 0 else "towards fine"
    print(f"  {name:<22} {weight:+.3f}  {direction}")
