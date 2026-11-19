import json
from pathlib import Path

import requests

import app as shop

STUB = json.loads((Path(__file__).parent.parent / "partner/mappings/catalog.json").read_text())


class FakeResponse:
    def __init__(self, status, body=None):
        self.status_code = status
        self._body = body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Server Error")

    def json(self):
        return self._body


def fake_partner(monkeypatch, respond):
    calls = []

    def get(url, timeout):
        calls.append((url, timeout))
        return respond()

    monkeypatch.setattr(shop.requests, "get", get)
    return calls


def test_price_comes_from_the_partner_catalog(client, monkeypatch):
    calls = fake_partner(monkeypatch, lambda: FakeResponse(200, STUB["response"]["jsonBody"]))

    r = client.get("/price/MK-II")

    assert r.status_code == 200
    assert r.get_json()["price"] == "1234.56"
    assert r.get_json()["currency"] == "UAH"
    assert calls == [(f"{shop.PARTNER_URL}/v1/catalog/MK-II", shop.PARTNER_TIMEOUT)]


def test_partner_error_is_a_502_not_a_crash(client, monkeypatch):
    fake_partner(monkeypatch, lambda: FakeResponse(500))

    r = client.get("/price/MK-II")

    assert r.status_code == 502
    assert r.get_json()["error"] == "HTTPError"


def test_partner_timeout_is_a_502(client, monkeypatch):
    def slow():
        raise requests.Timeout("read timed out")

    fake_partner(monkeypatch, slow)

    r = client.get("/price/MK-II")

    assert r.status_code == 502
    assert r.get_json()["error"] == "Timeout"
