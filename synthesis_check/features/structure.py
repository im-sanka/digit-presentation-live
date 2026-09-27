"""Structure features: the things that actually sink an order.

Repeats confuse the assembler, hairpins stop the polymerase, homopolymer and
dinucleotide runs make it lose count. Brute force throughout: the longest
construct in the file is a few hundred bases, so the O(n^2) scans finish
before you have finished saying the word "features".
"""

from __future__ import annotations

from .sequence import rev_comp


def longest_repeat(seq: str) -> tuple[int, int]:
    """Longest substring that appears more than once, and how often it appears.

    The strongest single predictor in the published feature analyses: a
    synthesiser assembles overlapping fragments, and two identical stretches
    give it a wrong pair to join.
    """
    for length in range(len(seq) // 2, 3, -1):
        seen: dict[str, int] = {}
        for i in range(len(seq) - length + 1):
            key = seq[i : i + length]
            seen[key] = seen.get(key, 0) + 1
        best = max(seen.values())
        if best > 1:
            return length, best
    return 0, 0


def hairpin(seq: str) -> int:
    """Longest stem that could fold back on itself further along the strand."""
    best = 0
    for length in range(4, len(seq) // 2 + 1):
        for i in range(len(seq) - length + 1):
            if seq.find(rev_comp(seq[i : i + length]), i + length) != -1:
                best = length
                break
    return best


def homopolymer(seq: str) -> int:
    """Longest run of one base. Polymerases slip on these and lose count."""
    best = run = 1
    for i in range(1, len(seq)):
        run = run + 1 if seq[i] == seq[i - 1] else 1
        best = max(best, run)
    return best


def dinucleotide(seq: str) -> int:
    """Longest (XY)n tract, in bases."""
    best = 0
    for i in range(len(seq) - 1):
        pair = seq[i : i + 2]
        if pair[0] == pair[1]:
            continue
        j = i
        while j + 2 <= len(seq) and seq[j : j + 2] == pair:
            j += 2
        best = max(best, j - i)
    return best
