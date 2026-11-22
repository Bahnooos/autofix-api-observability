# Incident Response Runbook — AutoFix Workshop API

## Alert: `HighRequestLatency`
- **Severity:** `warning`
- **PromQL Expression:** `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[1m])) by (le)) > 0.01`
- **For Duration:** `10s`
- **Summary:** High API p95 latency detected (> 10ms).

---

### 1. Diagnosis Steps
1. **Confirm the firing alert:**
   - Check Prometheus Alerts UI at `http://localhost:9090/alerts` or the Grafana Dashboard at `http://localhost:3000`.
2. **Identify the affected endpoint and request rate:**
   - Run the following PromQL query in Prometheus:
     ```promql
     sum(rate(http_requests_total[1m])) by (path, status)
     ```
3. **Inspect structured JSON logs:**
   - Check the FastAPI `stdout` logs for requests with elevated `latency` values:
     ```bash
     # View recent slow requests from API logs
     grep '"latency"' api.log | tail -n 20
     ```
4. **Check system and process load:**
   - Verify CPU/memory usage and active connections on the host:
     ```bash
     top -b -n 1 | head -n 15
     ```

---

### 2. Resolution / Mitigation Steps
1. **Mitigate traffic spikes (Immediate):**
   - Increase Uvicorn worker processes to handle concurrent requests across multiple CPU cores:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
     ```
   - Put a reverse proxy (Nginx) in front of the API with rate limiting or caching for `/metrics` if scraped aggressively.
2. **Verify Recovery:**
   - Monitor the p95 latency graph in Grafana (`http://localhost:3000`).
   - Confirm `HighRequestLatency` transitions from `FIRING` back to `INACTIVE` in `http://localhost:9090/alerts`.
