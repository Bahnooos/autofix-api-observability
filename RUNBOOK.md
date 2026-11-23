python3 -c '
content = """# Incident Response Runbook — AutoFix Workshop API

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
3. **Inspect structured JSON logs on stdout:**
   - Because the FastAPI service runs directly via Uvicorn and writes structured JSON logs to `stdout` (not a file), inspect the active Uvicorn terminal output directly (or filter the running process stdout if backgrounded):
     ```bash
     # Check active Uvicorn process and inspect stdout in the running terminal
     pgrep -af uvicorn
     ```
4. **Check system and process load:**
   - Verify CPU/memory usage and active connections on the host:
     ```bash
     top -b -n 1 | head -n 15
     ```

---

### 2. Resolution / Mitigation Steps
1. **Mitigate traffic spikes (Immediate):**
   - Restart Uvicorn with multiple worker processes to handle concurrent requests across CPU cores:
     ```bash
     pkill -f "uvicorn main:app"
     uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
     ```
2. **Verify Recovery:**
   - Monitor the p95 latency graph in Grafana (`http://localhost:3000`).
   - Confirm `HighRequestLatency` transitions from `FIRING` back to `INACTIVE` in `http://localhost:9090/alerts`.

---

### 3. Rollback & Escalation (If p95 Stays High)
- **Rollback:** If multi-worker startup causes port binding errors or memory exhaustion, revert immediately to the known-good single-worker command (`uvicorn main:app --host 0.0.0.0 --port 8000`) and rate-limit or pause any active load tests/upstream traffic spikes.
- **Next Action & Ownership:** If p95 latency remains above `10ms` for 5 minutes after scaling workers and verifying no synthetic load test is running, **escalate to the Backend/API Service Owner (DevOps & Backend On-Call Lead)** to profile blocking I/O or slow endpoint handlers in `main.py` and enable upstream rate limiting.
"""
open("RUNBOOK.md", "w").write(content)
' && git add RUNBOOK.md && git commit -m "fix(runbook): replace api.log with uvicorn stdout check and add rollback/escalation path" && git push origin main