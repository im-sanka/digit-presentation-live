"""The number on stage is the number in the README."""

import pytest

from synthesis_check.model import check, fit, load_orders, loo_accuracy, weights


@pytest.fixture(scope="module")
def orders():
    return load_orders()


def test_file_shape(orders):
    assert len(orders) == 44
    assert (orders.synthesised == "no").sum() == 20


def test_leave_one_out_accuracy(orders):
    assert loo_accuracy(orders) == pytest.approx(0.886, abs=0.001)


def test_model_uses_the_features_the_literature_does(orders):
    top = set(weights(fit(orders)).head(3).index)
    assert top == {"hairpin_stem", "longest_repeat", "homopolymer_max"}


def test_check_gives_reasons_in_scientist_units(orders):
    model = fit(orders)
    bad = check(model, orders.loc[orders.synthesised == "no", "sequence"].iloc[0])
    good = check(model, orders.loc[orders.synthesised == "yes", "sequence"].iloc[0])
    assert bad["likely_to_fail"] and any("repeat" in r for r in bad["reasons"])
    assert not good["likely_to_fail"] and good["reasons"] == []
