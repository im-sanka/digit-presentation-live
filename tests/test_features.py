"""The nasty sequence must look worse than the real gene."""

from synthesis_check.features import COLUMNS, clean, featurise
from synthesis_check.features.structure import dinucleotide, hairpin, homopolymer, longest_repeat

GENE = "ATGAGTAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAATTAGATGGTGATGTT"
NASTY = "GGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCC"


def test_every_column_accounted_for():
    assert list(featurise(GENE)) == COLUMNS


def test_nasty_looks_nasty():
    ok, bad = featurise(GENE), featurise(NASTY)
    assert bad["longest_repeat"] > ok["longest_repeat"]
    assert bad["gc_content"] > ok["gc_content"]
    assert ok["length"] == len(GENE)


def test_structure_features_on_known_strings():
    assert longest_repeat("ACGTACGT") == (4, 2)
    assert homopolymer("ACGGGGT") == 4
    assert dinucleotide("AGTGTGTGTC") == 8
    assert hairpin("GGGGCCCCTTTTGGGGCCCC") >= 8


def test_clean_strips_fasta_noise():
    assert clean(">seq1\nacg t\n123 NNN") == "ACGT"
