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
