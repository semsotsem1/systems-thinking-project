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
- Target load is intentionally limited to 300–500 rps to keep experiments reproducible.
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

- `GET /health` reports degraded status
- JWT auth protects `/data/*` endpoints

**Planned endpoints (draft)**

- `GET /health`
- `POST /auth/login`
- `CRUD /items or /notes`

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
  "path": "/items",
  "status_code": 503,
  "db_unavailable": true
}
```

**During DB outage:**
- `db_errors_total` increases
- error rate spikes (4xx/5xx)
- all data endpoints return 503
- logs contain `db_unavailable=true`

**Impact**
All data endpoints return 503 responses. The system doesn't try to hide its failures, but it remains predictable and observable in its behavior.

**Recovery**
Once the database connection is recovered, the system will then automatically resume normal operation without manual intervention.

**Mitigation (planned)**
- Fast DB timeout (<1s) to avoid hanging requests
- Fail-fast behavior: return 503 on data endpoints during DB outage
- Optional read-only mode from in-memory cache (if safe to serve stale data)
- Separate read/write paths to isolate failures and analyze degradation clearly
- Circuit breaker (stretch goal) to prevent repeated DB retries in case of outage

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

- **Week 1:** Creating a FastAPI skeleton, adding SQLite integration, basic auth decision
- **Week 2:** Logging, metrics collection, load testing scripts
- **Week 3:** Database outage scenario and degraded mode
- **Week 4:** Anomaly detection (z-score), unit tests, probability/stats integration
- **Week 5:** Security hardening and ISC2 CC completion
- **Week 6:** SOP draft and documentation polishing
- **Week 7:** Final package and submission
