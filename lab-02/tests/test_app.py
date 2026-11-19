import app as shop


def test_health_answers_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_data(as_text=True) == "ok\n"


def test_visits_start_at_one_and_count_up(client):
    assert client.get("/visits").get_json() == {"visits": 1, "store": "file"}
    assert client.get("/visits").get_json() == {"visits": 2, "store": "file"}


def test_visits_continue_from_what_is_on_disk(client, counter):
    counter.write_text("41")
    assert client.get("/visits").get_json()["visits"] == 42
    assert counter.read_text() == "42"


def test_ready_names_the_file_store(client, counter):
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.get_json() == {"ready": True, "store": f"file:{counter}"}


def test_ready_and_visits_are_503_when_the_store_is_unusable(client, monkeypatch, tmp_path):
    not_a_dir = tmp_path / "blocker"
    not_a_dir.write_text("")
    monkeypatch.setattr(shop, "COUNTER_FILE", not_a_dir / "visits.txt")

    ready = client.get("/ready")
    assert ready.status_code == 503
    assert ready.get_json()["ready"] is False

    visits = client.get("/visits")
    assert visits.status_code == 503
    assert visits.get_json()["store"] == "file"
