"""Composition features: what the sequence is made of.

Everything here is a plain function of the string, with no state and no lab.
"""

from __future__ import annotations

COMPLEMENT = {"A": "T", "T": "A", "G": "C", "C": "G"}

#: the window the GC extremes are measured over, in bases
WINDOW = 50

#: how many bases a vendor builds in one piece, for the fragment count
FRAGMENT = 40


def rev_comp(seq: str) -> str:
    """Reverse complement, so a hairpin can be found by searching for its partner."""
    return "".join(COMPLEMENT.get(b, b) for b in reversed(seq))


def gc(seq: str) -> float:
    """GC as a percentage. The one number everybody already knows."""
    return 100.0 * sum(b in "GC" for b in seq) / len(seq)


def tm(seq: str) -> float:
    """GC-corrected melting temperature (Wallace-style, salt-adjusted form)."""
    return 64.9 + 41.0 * (sum(b in "GC" for b in seq) - 16.4) / len(seq)


def windows(seq: str, width: int = WINDOW) -> list[float]:
    """GC of every window of `width`, so the worst stretch cannot hide in a mean."""
    if len(seq) < width:
        return [gc(seq)]
    return [gc(seq[i : i + width]) for i in range(len(seq) - width + 1)]
