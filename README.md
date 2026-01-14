# systems-thinking-project
API prototype with metrics, load tests (500 rps), and a documented failure scenario

### Problem statement

Like many real-world systems, API-based services often run smoothly under normal conditions but can fail in unclear ways under load, partial outages and unexpected inputs.
As a newbie in systems engineering, I want to understand how failures, performance limits, and security decisions affect how a system behaves.

This project is a small API designed to explore reliability, observability and basic security trade-offs in a controlled environment.

### Target user

Beginners who want to understand how API-based systems work under real-world limitations such as load, failures, and basic security requirements.

### Success metrics

- The API responds within allowable time limits under average load (300-500 requests per second).
- The number of errors remains low during normal operation.
- When the database becomes unavailable, the system continues to operate in a degraded and at the same time predictable way.

### Constraints

- The system is intentionally kept simple to make design decisions easier to understand and discuss.
- Performance requirements are limited to moderate load (300–500 requests per second).
- Security is implemented at a basic level, focusing on clear and understandable mechanisms rather than completeness.

### Key trade-offs

**JWT vs server-side sessions**

JWT was chosen for simplicity and statelessness. It makes the system easier to scale and reason about, but comes with security trade-offs such as token theft and limited server-side control.

**SQLite vs PostgreSQL**

SQLite was chosen to reduce operational complexity and keep the focus on system behavior rather than database management. This limits scalability and concurrency but is sufficient for controlled experiments.

**In-memory queue vs external message broker**

An in-memory queue is used to keep the architecture simple and transparent. External brokers like Redis or RabbitMQ would provide better reliability but add operational and conceptual complexity.

### Failure scenario: database outage

**Trigger**  
The database becomes unavailable due to an unexpected shutdown or a connection error.

**Detection**  
The API logs database connection errors and exposes a degraded status through the health endpoint.

**Impact**  
Write operations fail and return errors, while read operations may return cached or stale data. Overall, system functionality is reduced but remains predictable.

**Recovery**  
When the database connection is restored, the system resumes normal operation without manual intervention.

**Future improvements**  
Possible improvements include better caching strategies, retry mechanisms, and a clearer separation between read and write paths.

### Observability plan

The following signals are collected to understand system behavior:

- **Request rate** to know how much traffic the system handles.
- **Error rate (4xx/5xx)** for abnormal behavior detection and failures.
- **Latency (p50, p95)** to understand how response times change under load.
- **Basic logs** with request identifiers to trace individual requests during failures. 

These signals are designed to be simple so that the behavior of the system is easy to observe and reason about.
