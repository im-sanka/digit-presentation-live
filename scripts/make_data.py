"""Build the order file.

The real file is a few dozen rows of customer constructs and it is not going in
a public repo, which is the whole argument of the talk. So this writes a
stand-in with the same shape and the same failure modes: real gene fragments
that a vendor would build without complaint, and constructs carrying the things
that actually sink an order — tandem repeats, GC-rich blocks, homopolymer runs,
dinucleotide tracts, hairpins.

Seeded, so the file is the same every time and the number you rehearse with is
the number you get on stage.

    python3 -m scripts.make_data
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

# The Aequorea victoria GFP CDS, AAA27721.1 from ENA. A real gene, so the
# "fine" rows look like something a vendor really was asked to make.
GFP = (
    "ATGAGTAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAATTAGATGGTGATGTTAATGGGCACAAATTTTCTGTCAGTGGAGAG"
    "GGTGAAGGTGATGCAACATACGGAAAACTTACCCTTAAATTTATTTGCACTACTGGAAAACTACCTGTTCCATGGCCAACACTTGTCACTACTTTC"
    "TCTTATGGTGTTCAATGCTTTTCAAGATACCCAGATCATATGAAACAGCATGACTTTTTCAAGAGTGCCATGCCCGAAGGTTATGTACAGGAAAGA"
    "ACTATATTTTTCAAAGATGACGGGAACTACAAGACACGTGCTGAAGTCAAGTTTGAAGGTGATACCCTTGTTAATAGAATCGAGTTAAAAGGTATT"
    "GATTTTAAAGAAGATGGAAACATTCTTGGACACAAATTGGAATACAACTATAACTCACACAATGTATACATCATGGCAGACAAACAAAAGAATGGA"
    "ATCAAAGTTAACTTCAAAATTAGACACAACATTGAAGATGGAAGCGTTCAACTAGCAGACCATTATCAACAAAATACTCCAATTGGCGATGGCCCT"
    "GTCCTTTTACCAGACAACCATTACCTGTCCACACAATCTGCCCTTTCGAAAGATCCCAACGAAAAGAGAGACCACATGGTCCTTCTTGAGTTTGTA"
    "ACAGCTGCTGGGATTACACATGGCATGGATGAACTATACAAATAA"
)

# The seven the slides show, so rows 1-7 of the file are the ones the room
# has already read.
FROM_THE_SLIDES = [
    ("ATGAGTAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAATTAGATGGTGATGTT", "yes", "yes"),
    ("GGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCC", "no", "no"),
    ("AAAGATGACGGGAACTACAAGACACGTGCTGAAGTCAAGTTTGAAGGTGATACCCTTGTTAATAGAATCGAGTTAAAAGGTATT", "yes", "yes"),
    ("CAGGTCACCGGTAAAGGCTTTTCCAGGTCACCGGTAAAGGCTTTTCGCGGCCGCGGCCGCGGCCGC", "no", "no"),
    ("ATCAAAGTTAACTTCAAAATTAGACACAACATTGAAGATGGAAGCGTTCAACTAGCAGACCATTATCAACAAAATACTCCAATTGGCGAT", "yes", "yes"),
    ("CGCCGCCCGCCGCCCGCCGCCCGCCGCCCGCCGCCGGGGGGGGGGCCCCCCCCCGCGCGCGCGCGC", "no", "no"),
    ("CTGTCCACACAATCTGCCCTTTCGAAAGATCCCAACGAAAAGAGAGACCACATGGTCCTTCTTGAGTTTGTA", "yes", "yes"),
]

COMPLEMENT = {"A": "T", "T": "A", "G": "C", "C": "G"}


def rev_comp(seq: str) -> str:
    return "".join(COMPLEMENT[b] for b in reversed(seq))


def gene_slice(rng: random.Random, low: int = 66, high: int = 150) -> str:
    """A stretch of the real gene: the kind of order that comes back fine."""
    length = rng.randrange(low, high, 3)
    start = rng.randrange(0, len(GFP) - length)
    return GFP[start : start + length]


def tandem(rng: random.Random) -> str:
    """The same unit over and over. The assembler has no way to tell them apart."""
    unit = "".join(rng.choice("ACGT") for _ in range(rng.randint(6, 14)))
    body = unit * rng.randint(6, 10)
    return (gene_slice(rng, 24, 40) + body)[:150]


def gc_block(rng: random.Random) -> str:
    """A stretch the polymerase stalls on."""
    body = "".join(rng.choice(["GGC", "GCC", "CGG", "CCG"]) for _ in range(rng.randint(18, 30)))
    return (gene_slice(rng, 24, 40) + body)[:150]


def homopolymer_run(rng: random.Random) -> str:
    """Ten of the same base in a row, and the polymerase loses count."""
    base = rng.choice("ACGT")
    seq = gene_slice(rng, 60, 100)
    cut = len(seq) // 2
    return seq[:cut] + base * rng.randint(10, 14) + seq[cut:]


def dinuc_tract(rng: random.Random) -> str:
    """(GT)n and friends: easy to synthesise wrong, hard to sequence through."""
    pair = rng.choice(["GT", "CA", "AG", "TC"])
    return (gene_slice(rng, 30, 50) + pair * rng.randint(14, 22))[:150]


def hairpin_pair(rng: random.Random) -> str:
    """A stem that folds back on itself and stops the reaction dead."""
    seq = gene_slice(rng, 60, 90)
    stem = "".join(rng.choice("GC") for _ in range(rng.randint(12, 18)))
    cut = len(seq) // 2
    return seq[:cut] + stem + "TTTT" + rev_comp(stem) + seq[cut:]


def borderline(rng: random.Random) -> str:
    """A real fragment with one mild problem in it.

    These are the rows that keep the score honest. Without them the two classes
    separate perfectly, the model scores 1.0, and nobody in the room believes a
    word of it.
    """
    seq = gene_slice(rng, 70, 110)
    repeated = seq[10:24]
    return seq + repeated


def main() -> None:
    rng = random.Random(11)
    rows = [{"sequence": s, "purity": p, "synthesised": m} for s, p, m in FROM_THE_SLIDES]

    for _ in range(16):
        rows.append({"sequence": gene_slice(rng), "purity": "yes", "synthesised": "yes"})

    for maker in (tandem, gc_block, homopolymer_run, dinuc_tract, hairpin_pair):
        for _ in range(3):
            rows.append({"sequence": maker(rng), "purity": "no", "synthesised": "no"})

    # a mild problem is not a death sentence: most of these still come back,
    # and two of them do not
    for i in range(6):
        rows.append(
            {
                "sequence": borderline(rng),
                "purity": "yes" if i > 1 else "no",
                "synthesised": "yes" if i > 1 else "no",
            }
        )

    # and a few that were built but came back dirty, so purity is its own
    # question rather than a copy of the other column
    for row in rows[8:12]:
        row["purity"] = "no"

    # slicing makes a copy, so shuffle the copy and put it back — otherwise
    # the file stays in the order it was built and every failure sits together
    tail = rows[7:]
    rng.shuffle(tail)
    rows[7:] = tail

    out = Path(__file__).resolve().parent.parent / "data" / "orders.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="") as fh:
        # LF, so regenerating the file does not show up as a diff
        writer = csv.DictWriter(
            fh, fieldnames=["sequence", "purity", "synthesised"], lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)

    failed = sum(r["synthesised"] == "no" for r in rows)
    print(f"wrote {out} — {len(rows)} orders, {failed} of them failed")


if __name__ == "__main__":
    main()
