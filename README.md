# AutoFix Workshop API — Monitoring, Alerting & Load Testing Stack

A containerized observability and load-testing stack built around a **FastAPI** service, **Prometheus**, **Grafana**, and **k6**, orchestrated using **Docker Compose**.

## Overview

This project provides a multi-container monitoring and alerting environment alongside an instrumented Python API, a k6 load test script, an incident response runbook, and a blameless postmortem.

The monitoring stack can be started using a single Docker Compose command.

## Features

- FastAPI application running on port `8000`
- Prometheus metrics instrumentation at `/metrics` (request counters and latency histograms)
- Structured JSON request logging to `stdout`
- Prometheus metrics scraper and alerting engine exposed on port `9090`
- Grafana visualization dashboard exposed on port `3000`
- `HighRequestLatency` alert rule (`p95 > 10ms` for `10s`)
- `k6` load testing script (`100` concurrent virtual users for `60s`)
- Incident response runbook (`RUNBOOK.md`) and blameless postmortem (`POSTMORTEM.md`)

## Project Structure

```text
flask-api-task/
├── .gitignore
├── alert_rules.yml
├── docker-compose.yml
├── loadtest.js
├── main.py
├── POSTMORTEM.md
├── prometheus.yml
├── requirements.txt
├── RUNBOOK.md
├── test_main.py
└── README.md
```

## Services

### FastAPI App

A Python FastAPI application that:

- Exposes `/health` for service health checks.
- Exposes `/metrics` in Prometheus text exposition format.
- Emits structured JSON access logs for every HTTP request.

### Prometheus

Uses the official `prom/prometheus:latest` image exposed on port `9090`:

- Scrapes `http://host.docker.internal:8000/metrics` every 5 seconds (`prometheus.yml`).
- Evaluates alerting rules defined in `alert_rules.yml`.

### Grafana

Uses the official `grafana/grafana:latest` image exposed on port `3000`:

- Connects to Prometheus at `http://prometheus:9090`.
- Visualizes p95 request latency and active alert states.

### k6 Load Generator

Runs `loadtest.js` against the API to simulate `100` concurrent virtual users over `60` seconds and verify alert triggering.

## Getting Started

### Prerequisites

- Python 3.10+
- Docker
- Docker Compose
- k6 (`v0.54.0`+)

### Start the monitoring stack

```bash
docker compose up -d
```

### Start the FastAPI application

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Check services

```bash
docker compose ps
```

### Stop the stack

```bash
docker compose down
```

## Access Points

- **FastAPI Service:** `http://localhost:8000`
- **FastAPI Metrics:** `http://localhost:8000/metrics`
- **Prometheus UI & Alerts:** `http://localhost:9090`
- **Prometheus Alerts:** `http://localhost:9090/alerts`
- **Grafana Dashboard:** `http://localhost:3000` (Login: `admin` / `admin`)

## API Endpoints

### `GET /health`

Returns service health status:

```json
{
  "status": "ok"
}
```

### `GET /metrics`

Returns Prometheus-formatted metrics, including:

- `http_requests_total`
- `http_request_duration_seconds_bucket`

## Alert Definitions

Defined in [`alert_rules.yml`](alert_rules.yml):

- **Alert Name:** `HighRequestLatency`
- **Expression:**
  ```promql
  histogram_quantile(
    0.95,
    sum(rate(http_request_duration_seconds_bucket[1m])) by (le)
  ) > 0.01
  ```
- **For Duration:** `10s`
- **Severity:** `warning`
- **Summary:** Fires when the 95th percentile (p95) HTTP request latency exceeds `10ms` (`0.01s`) for 10 consecutive seconds.

## Load Testing & Alert Verification

Run the k6 load test (`100` VUs for `60s`):

```bash
k6 run loadtest.js
```

During execution:

- `k6` validates HTTP 200 responses and prints latency percentiles (`avg`, `p(90)`, `p(95)`).
- The p95 latency rises above `10ms` (approximately `138ms` in the observed test), causing `HighRequestLatency` to transition from `INACTIVE` to `PENDING` and then `FIRING` in Prometheus (`http://localhost:9090/alerts`) and Grafana (`http://localhost:3000`).

## Incident Runbook & Postmortem

- **Incident Runbook:** See [`RUNBOOK.md`](RUNBOOK.md) for PromQL diagnostic queries, log inspection steps, and Uvicorn scaling mitigation (`--workers 4`) when `HighRequestLatency` fires.
- **Blameless Postmortem:** See [`POSTMORTEM.md`](POSTMORTEM.md) for the incident timeline, root cause analysis, and action items from the k6 load test.

## Useful Commands

```bash
# Start Prometheus and Grafana
docker compose up -d

# View running containers
docker compose ps

# View container logs
docker compose logs -f

# Run the k6 load test
k6 run loadtest.js

# Run unit tests
pytest -v

# Stop services
docker compose down
```

## Notes

- Prometheus reaches the host FastAPI service via `host.docker.internal:8000`, configured in `docker-compose.yml`.
- `prometheus.yml` and `alert_rules.yml` are mounted read-only into the Prometheus container.
- Refer to [`RUNBOOK.md`](RUNBOOK.md) for on-call triage whenever `HighRequestLatency` fires.

