# systems-thinking-project

API prototype with an emphasis on system behavior under load, errors, and basic security constraints.

### Problem statement

Like many real-world systems, API-based services can work well under normal conditions and fail in unclear ways when under load, partially down, or with unexpected inputs.

As a learner of systems engineering, I want to understand how failures, performance limits, and security decisions drive the way a system behaves. This project is a small API meant to explore reliability, observability, and basic security trade-offs within a controlled environment.

### Target user

Beginners who want to understand how API-based systems work under real-world limitations such as load, failures, and basic security requirements.

### How to run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Load test

```bash
python scripts/load_test.py
```

### Success metrics

- Baseline: 300 rps, p95 latency < 200ms, error rate < 1%
- Peak: 500 rps for 2 minutes, p95 latency < 300ms, error rate < 3%
- DB outage: data endpoints return 503, /health returns degraded=true, failure is observable via logs + metrics

### Constraints

- Keep the system as simple as possible in order to make decisions easy to comprehend and reason about.
- Target load is intentionally limited to 300–500 rps to keep experiments reproducible.
- Basic security only: clarity over completeness.

### Architecture (high level)

```
[Client]
   |
   v
[FastAPI API] ---> [SQLite DB]
   |
   +--> [Metrics middleware] --> [metrics_events (in-memory or SQLite)]
```

- `GET /health` reports degraded status
- JWT auth protects `/data/*` endpoints

**Planned endpoints (draft)**

- GET /health
- POST /auth/login
- CRUD /items or /notes

Scripts:
- /scripts/load_test.py drives traffic to the API 
- /scripts/anomaly_zscore.py analyzes exported metrics later

### Key trade-offs

**JWT vs server-side sessions**

JWT is used for simplicity and statelessness.
Trade-offs: token theft risk, hard to revoke tokens, limited server-side control.

**SQLite vs PostgreSQL**

SQLite has been used to minimize operational complexity and keep the focus of experiments on system behavior, not database management. This limits scalability but is sufficient for controlled experiments.

**In-memory metrics vs persistent storage**

Metrics are stored in memory or in a simple SQLite table to begin with. This keeps the observability mechanisms lightweight. Anything more heavy-duty would add complexity, not improve the learning results in this phase.

### Failure scenario: database outage

**Trigger**
The database will not be accessible because of the shutdown or connection error.

**Detection**
Errors in database connections are recorded, and the `GET /health` endpoint indicates that `degraded=true`.

**During DB outage:**

- db_errors_total increases
- error rate spikes
- logs contain db_unavailable=true

**Impact**
All data endpoints return 503 responses. The system doesn't try to hide its failures, but it remains predictable and observable in its behavior.

**Recovery**
Once the database connection is recovered, the system will then automatically resume normal operation without manual intervention.

**Future improvements**
Some potential improvements that can be made are read-only support for some endpoints, improved retry logic, and differentiating read and write paths.

### Observability plan

The following signals are collected to understand system behavior:

- **Request rate** to see the volume of incoming traffic.
- **Error rate (4xx/5xx)** to detect abnormal behavior and failures.
- **Latency (p50, p95)** to understand response time distribution under load.
- **Structured logs** with request identifiers to trace failures and degraded states.

Signals are intentionally kept minimal in order to make system behavior easy to observe and reason about.

### Non-goals

- No distributed architecture or Kubernetes
- No production-grade authentication (OAuth, MFA, SSO)
- No external message brokers (Redis, RabbitMQ)
- No multi-region high availability

### Plan of execution

Week 1: Creating a FastAPI skeleton, adding SQLite integration, basic auth decision
Week 2: Logging, metrics collection, load testing scripts
Week 3: Database outage scenario and degraded mode
Week 4: Script for anomaly detection and unit tests
Week 5: Security hardening and ISC2 CC completion
Week 6: SOP draft and documentation polishing
Week 7: Final package and submission
