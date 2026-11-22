# Blameless Postmortem — High API Latency During Load Test

- **Date:** November 22, 2026
- **Severity:** Warning (`HighRequestLatency`)
- **Duration:** ~60 seconds (Controlled `k6` load test window)
- **Author:** Ahmed Essam-Eldin El-Bahnasawy

---

## 1. Summary
During a scheduled `k6` load test simulating **100 concurrent virtual users (VUs) over 60 seconds** against `http://localhost:8000/metrics`, the AutoFix Workshop API's 95th percentile (p95) latency spiked from `< 1ms` to **`137.8ms` (`0.1378s`)**, breaching the `10ms` (`0.01s`) threshold. Prometheus detected the breach and transitioned the `HighRequestLatency` alert to `FIRING` after 10 seconds. All HTTP requests returned `200 OK` with zero dropped connections, and latency returned to baseline immediately after the test ended.

---

## 2. Timeline
- **T+00s:** Baseline verified (`autofix-api` target `UP` in Prometheus; `HighRequestLatency` `INACTIVE`).
- **T+05s:** Executed `k6 run loadtest.js` (`100 VUs`, `60s` duration) targeting `/metrics`.
- **T+15s:** Concurrent request saturation pushed p95 latency above `0.01s`; alert entered `PENDING` state.
- **T+25s:** High latency persisted past the `10s` evaluation window; `HighRequestLatency` transitioned to **`FIRING`** (observed p95 value: `0.1378s`).
- **T+65s:** `k6` test completed; request queue drained and p95 latency dropped back below `0.01s`.
- **T+75s:** Prometheus automatically resolved `HighRequestLatency` to `INACTIVE`.

---

## 3. Root Cause
- **Single-Process Uvicorn Execution:** The FastAPI service was running with a single worker process (`uvicorn main:app --port 8000`), causing 100 concurrent requests to contend for a single Python event loop and serializing `/metrics` metric-generation calls.

---

## 4. Lessons Learned & Action Items
| Action Item | Priority | Status |
| :--- | :--- | :--- |
| Run Uvicorn with multiple worker processes (`--workers 4`) for production concurrency | High | Planned |
| Document step-by-step triage and mitigation commands in `RUNBOOK.md` | High | Completed |
| Keep Prometheus scrape intervals and alert thresholds tuned to realistic production SLOs | Medium | Completed |
