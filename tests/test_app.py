"""The app, driven the way a scientist drives it: press a button, read the verdict."""

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture(scope="module")
def app():
    return AppTest.from_file("frontend/app.py").run()


def test_loads_without_error(app):
    assert not app.exception
    assert "Should be fine" in app.success[0].value


def test_each_example_gives_the_verdict_on_the_slide(app):
    expected = ["Should be fine", "Likely to fail", "Likely to fail"]
    for button, verdict in zip(app.button, expected):
        button.click().run()
        assert verdict in (list(app.success) + list(app.error))[0].value


def test_short_input_asks_for_more(app):
    app.text_area[0].set_value("ACGT").run()
    assert "at least 40 bases" in app.info[0].value
