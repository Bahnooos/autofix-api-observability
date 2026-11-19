# AutoFix Workshop API — Observability & Metrics (Task 2)

A lightweight FastAPI service built with production observability foundations: health checks, Prometheus metrics instrumentation, structured JSON logging, and automated unit tests.

## Project Structure

```text
.
├── main.py              # FastAPI app, Prometheus metrics, and JSON logging middleware
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container image definition
├── .gitignore
└── tests/
    └── test_main.py     # Pytest suite for endpoints and structured logs