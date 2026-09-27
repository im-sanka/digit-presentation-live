"""The HTTP API answers what the app answers."""

from fastapi.testclient import TestClient

from synthesis_check.api import app

client = TestClient(app)
NASTY = "GGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCCGGCGCC"


def test_health():
    assert client.get("/health").json() == {"ok": True}


def test_check_returns_a_verdict_with_reasons():
    body = client.post("/check", json={"sequence": NASTY}).json()
    assert body["likely_to_fail"] is True
    assert any("repeat" in r for r in body["reasons"])
    assert len(body["features"]) == 12


def test_short_sequence_is_rejected():
    assert client.post("/check", json={"sequence": "ACGT"}).status_code == 422
