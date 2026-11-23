# AutoFix Workshop API — Monitoring, Alerting & Load Testing

A containerized FastAPI service instrumented with Prometheus metrics and structured JSON logging, monitored via Prometheus and Grafana using Docker Compose, and load-tested with `k6`.

## Project Structure

```text
.
├── main.py                # FastAPI application (/health, /metrics, structured JSON logs)
├── requirements.txt       # Python dependencies
├── test_main.py           # Automated unit tests (pytest)
├── docker-compose.yml     # Prometheus & Grafana monitoring stack
├── prometheus.yml         # Prometheus scrape configuration (5s interval)
├── alert_rules.yml        # HighRequestLatency alert definition
├── loadtest.js            # k6 load test script (100 concurrent VUs for 60s)
├── RUNBOOK.md             # Incident response & mitigation runbook
├── POSTMORTEM.md          # Blameless postmortem from the k6 load test incident
└── README.md              # Deployment, alerting, and handover documentation