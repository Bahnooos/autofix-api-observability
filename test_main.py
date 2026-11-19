import json
import logging

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_exposes_counter_and_histogram():
    client.get("/health")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text


def test_json_log_contains_required_fields(caplog):
    with caplog.at_level(logging.INFO, logger="autofix_workshop"):
        response = client.get("/health")
        assert response.status_code == 200

    assert len(caplog.records) >= 1
    log_entry = json.loads(caplog.records[-1].getMessage())
    assert log_entry["method"] == "GET"
    assert log_entry["path"] == "/health"
    assert log_entry["status"] == 200
    assert "latency" in log_entry
    assert isinstance(log_entry["latency"], float)