"""The twelve features, computed from the sequence and nothing else.

These are the same twelve the slides show, with the same arithmetic, so a
number on stage matches the number on the slide behind it.

    from synthesis_check.features import features
    X = features(df.sequence)
"""

from __future__ import annotations

import pandas as pd

from .sequence import FRAGMENT, gc, tm, windows
from .structure import dinucleotide, hairpin, homopolymer, longest_repeat

#: column order, and the order they appear on the slides
COLUMNS = [
    "longest_repeat",
    "repeat_count",
    "gc_content",
    "max_window_gc",
    "min_window_gc",
    "tm",
    "tm_spread",
    "hairpin_stem",
    "homopolymer_max",
    "dinucleotide_repeat",
    "length",
    "fragments",
]


def clean(sequence: str) -> str:
    """Keep only A, C, G and T, upper-cased. Whitespace, numbers and FASTA noise go."""
    return "".join(c for c in sequence.upper() if c in "ACGT")


def featurise(seq: str) -> dict[str, float]:
    """One construct in, twelve numbers out."""
    seq = seq.strip().upper()
    win = windows(seq)
    rep_len, rep_count = longest_repeat(seq)
    pieces = [seq[i : i + FRAGMENT] for i in range(0, len(seq), FRAGMENT)]
    tms = [tm(p) for p in pieces if len(p) > 10] or [tm(seq)]
    return {
        "longest_repeat": rep_len,
        "repeat_count": rep_count,
        "gc_content": round(gc(seq), 1),
        "max_window_gc": round(max(win), 1),
        "min_window_gc": round(min(win), 1),
        "tm": round(tm(seq), 1),
        "tm_spread": round(max(tms) - min(tms), 1),
        "hairpin_stem": hairpin(seq),
        "homopolymer_max": homopolymer(seq),
        "dinucleotide_repeat": dinucleotide(seq),
        "length": len(seq),
        "fragments": -(-len(seq) // FRAGMENT),  # ceiling division
    }


def features(sequences) -> pd.DataFrame:
    """A column of sequences in, a twelve column frame out.

    This is the whole "one column becomes twelve" slide.
    """
    return pd.DataFrame([featurise(s) for s in sequences], columns=COLUMNS)


__all__ = ["COLUMNS", "clean", "featurise", "features"]
