# systems-thinking-project

API prototype with an emphasis on system behavior under load, errors, and basic security constraints.

### Problem statement

Like many real-world systems, API-based services can work well under normal conditions and fail in unclear ways when under load, partially down, or with unexpected inputs.

As a learner of systems engineering, I want to understand how failures, performance limits, and security decisions drive the way a system behaves. This project is a small API meant to explore reliability, observability, and basic security trade-offs within a controlled environment.

### Target user

CS students and early engineers who want to understand how API-based systems work under real-world limitations such as load, failures, and basic security requirements.

### How to run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Load test

```bash
python scripts/load_test.py
```

## Evidence (will be updated weekly)

- Done: API skeleton + `/health` (pytest + ruff)
- Done: SQLite integration + Notes CRUD (+ tests, Swagger manual check)

- PR: JWT auth (TODO)
- PR: metrics middleware + `/metrics/summary` (TODO)
- Report: load test results table + plot (TODO)
- Evidence: DB outage run (logs + metrics) (TODO)
- Script: micro z-score anomaly detection + test (TODO)
- Script: network health checker + report (TODO)
- Doc: docs/runbook.md (TODO)

## Targets + Measurement setup (draft)

These are initial targets. Final numbers will be updated after running reproducible load tests on my machine.

### Load test scenarios (draft targets)

| Scenario | Duration | Target outcome (draft) |
|---|---:|---|
| Baseline | 60–120s | stable p95 latency and low error rate |
| Peak | 120s | higher p95 latency allowed, error rate still controlled |
| DB outage | 60–120s | data endpoints return 503 fast, `/health` reports `degraded=true`, spike visible in metrics |

### Measurement setup (to be filled once implemented)

- Machine: TODO (CPU/RAM/OS)
- Server: uvicorn workers = TODO
- Client/load tool: `scripts/load_test.py`
- Traffic mix: TODO (e.g., 80% GET / 20% POST)
- Notes: SQLite limitations may dominate write-heavy scenarios

### Constraints

- Keep the system as simple as possible in order to make decisions easy to comprehend and reason about.
- Target load is intentionally limited (draft: ~300-500 rps) to keep experiments reproducible on a single machine.
- Basic security only: clarity over completeness.

### Architecture

```
┌──────────┐
│  Client  │
└─────┬────┘
      │ HTTP requests
      ▼
┌───────────────────────┐
│     FastAPI API       │
│  + Metrics middleware │
└──┬────┬────┬────┬─────┘
   │    │    │    │
   │    │    │    └─────> GET /health (degraded status)
   │    │    └──────────> Structured logs (request_id, latency_ms, errors)
   │    └───────────────> Metrics store (in-memory or SQLite)
   └────────────────────> SQLite DB
```

**Note:** This is intentionally a monolith. Distributed components would obscure failure modes that I'm trying to understand clearly.

- `GET /health` reports system status (planned: includes `degraded=true/false`)
- JWT auth protects the Notes API endpoints (`/notes`, `/notes/{id}`) (planned)

## Planned endpoints (draft)

Public:
- `GET /health`
- `POST /auth/login`

Protected (JWT):
- `GET /notes`
- `POST /notes`
- `GET /notes/{id}`
- `PUT /notes/{id}`
- `DELETE /notes/{id}`

Scripts:
- /scripts/load_test.py drives traffic to the API 
- /scripts/anomaly_zscore.py analyzes exported metrics later

### Key trade-offs

**JWT vs server-side sessions**

Decision: JWT for simplicity and statelessness.

**Trade-offs:**
- ✅ Stateless → no session store needed, easier to reason about
- ✅ Scalable → tokens validated without DB lookup
- ❌ Token theft risk → mitigated with short expiry (15 min)
- ❌ Hard to revoke → logged-out users still have valid tokens until expiry
- ❌ Token size → JWTs are larger than session IDs in headers

**Why not sessions?**
Sessions would be more secure (server-side revocation), but add complexity:
- Need session store (Redis/DB)
- Harder to reason about distributed scenarios later

For the purpose of learning, simplicity favors JWT.

**SQLite vs PostgreSQL**

Decision: SQLite has been used to minimize operational complexity and keep the focus of experiments on system behavior, not database management. This limits scalability but is sufficient for controlled experiments.

**Trade-offs:**
- ✅ Zero configuration → single file, no server to manage
- ✅ Reproducible → same behavior across environments
- ✅ Fast for <500 rps → sufficient for controlled experiments
- ❌ Single-writer limitation → concurrent writes serialize
- ❌ No network access → can't separate API and DB layers

**Why not PostgreSQL?**
PostgreSQL would handle concurrency better and scale further, but:
- Adds setup complexity (installation, user management, connection pooling)
- Requires external service management
- Makes failure scenarios harder to reproduce (network issues, connection pools)
- Distracts from the core goal: understanding system behavior, not database administration

SQLite's limitations are well-understood and acceptable for 300–500 rps. If concurrent write bottlenecks appear during testing, that becomes a learning opportunity, not a problem.

**In-memory metrics vs persistent storage**

Decision: In-memory storage (or simple SQLite table) for metrics collection.

**Trade-offs:**
- ✅ Lightweight → no external dependencies (Prometheus, Grafana, InfluxDB)
- ✅ Easy to reason about → metrics are just data structures or DB rows
- ✅ Fast iteration → no setup, configuration, or network calls
- ❌ Lost on restart → metrics don't persist across API restarts
- ❌ No real-time dashboards → must export and analyze manually
- ❌ Not production-ready → would need proper time-series DB at scale

**Why not Prometheus + Grafana?**
A full monitoring stack would be more "realistic," but:
- Adds significant setup time (Docker Compose, configuration files)
- Obscures the core metrics logic behind abstractions
- Makes debugging harder (is the issue in my code or the monitoring stack?)
- Too much for a 7-week learning project

**Pattern**
I prioritize simplicity over production realism, with explicit limitations documented.

### Failure scenario: database outage

**Trigger**
The database will not be accessible because of the shutdown or connection error.

**Detection**
Errors in database connections are recorded, and the `GET /health` endpoint indicates that `degraded=true`.

Example log entry during outage:
```json
{
  "timestamp": "<ISO8601>",
  "level": "ERROR",
  "event": "db_connection_failed",
  "request_id": "abc-123",
  "path": "/notes",
  "status_code": 503,
  "db_unavailable": true
}
```

**During DB outage (expected):**
- 5xx error rate spikes
- `/health` shows `degraded=true`
- logs contain `db_unavailable=true`
- metrics summary shows increased failures and changed latency distribution

**Impact**
All data endpoints return 503 responses. The system doesn't try to hide its failures, but it remains predictable and observable in its behavior.

**Recovery**
Once the database connection is recovered, the system will then automatically resume normal operation without manual intervention.

**Mitigation (planned)**
- Fast DB timeout (<1s) to avoid hanging requests
- Fail-fast behavior: return 503 on data endpoints during DB outage
- Clear degraded signaling in `/health`
- Circuit breaker (stretch goal)

### Observability plan

The following signals are collected to understand system behavior:
- **Request rate** to see the volume of incoming traffic
- **Error rate (4xx/5xx)** to detect abnormal behavior and failures
- **Latency (p50, p95)** to understand response time distribution under load
- **Structured logs** with request identifiers to trace failures and degraded states

**Why these metrics and not others?**
These four signals (rate, errors, latency, logs) form the minimal viable observation set. Even more metrics such as CPU, memory, or disk I/O would be valuable in production, but for controlled experiments they would add noise without improving my understanding of API behavior.

Signals are intentionally kept minimal in order to make system behavior easy to observe and reason about.

### Non-goals

- No distributed architecture or Kubernetes
- No production-grade authentication (OAuth, MFA, SSO)
- No external message brokers (Redis, RabbitMQ)
- No multi-region high availability

### Known limitations

- **No refresh tokens**
   JWTs expire after 15 minutes; users must re-login.

- **SQLite concurrency limits**
   Concurrent writes serialize due to SQLite single-writer behavior.

- **Metrics may be in-memory**
   Metrics are lost on restart unless persisted to SQLite.

- **No per-endpoint rate limiting**
   Rate limiting (if added) is global for simplicity.

### Plan of execution

- **Week 1:** repo setup, docs cleanup, test baseline
- **Week 2:** FastAPI + SQLite + CRUD + JWT + basic tests
- **Week 3:** structured logs, metrics capture, load test script, results report (table + 1 plot)
- **Week 3.5:** network health checker (targets config + JSON/CSV report)
- **Week 4:** failure scenario - DB outage → degraded mode, evidence capture (logs + metrics)
- **Week 5:** security hardening + micro z-score script + final polishing + SOP v1
- **Week 6 (buffer):** debugging, documentation polish, final package and screenshots
