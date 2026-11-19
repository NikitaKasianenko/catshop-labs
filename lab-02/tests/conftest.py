import pytest

import app as shop


@pytest.fixture
def counter(tmp_path, monkeypatch):
    path = tmp_path / "visits.txt"
    monkeypatch.setattr(shop, "COUNTER_FILE", path)
    monkeypatch.setattr(shop, "DATABASE_URL", None)
    return path


@pytest.fixture
def client(counter):
    shop.app.config["TESTING"] = True
    return shop.app.test_client()
