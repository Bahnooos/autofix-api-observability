import json
import logging
import sys
import time
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("autofix_workshop")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(handler)
    logger.propagate = True
    return logger


logger = setup_logger()

REQUEST_COUNTER = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)

app = FastAPI(title="AutoFix Workshop API")


@app.middleware("http")
async def observability_middleware(request: Request, call_next) -> Response:
    start_time = time.perf_counter()
    response = await call_next(request)
    latency = time.perf_counter() - start_time

    method = request.method
    path = request.url.path
    status_code = response.status_code

    REQUEST_COUNTER.labels(method=method, path=path, status=str(status_code)).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(latency)

    log_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "path": path,
        "status": status_code,
        "latency": round(latency, 6),
    }
    logger.info(json.dumps(log_payload))
    return response


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse(status_code=200, content={"status": "ok"})


@app.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/repair-orders")
async def repair_orders() -> JSONResponse:
    return JSONResponse(status_code=200, content={"orders": []})