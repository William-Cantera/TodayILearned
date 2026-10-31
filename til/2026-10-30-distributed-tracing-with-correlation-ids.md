# TIL: Distributed Tracing with Correlation IDs

*Date: 2026-10-30*

## Summary / Problem Statement

When a single user request fans out across multiple microservices, debugging failures becomes a nightmare. Log files from Service A, B, and C each tell a partial story — but without a common thread, correlating events across services is nearly impossible. Distributed tracing with **Correlation IDs** solves this by tagging every log entry and downstream call with a shared unique identifier.

---

## Key Concepts & Technical Details

- **Correlation ID**: A unique identifier (typically a UUID) generated at the entry point of a request — usually an API gateway or the first service in the chain.

- **Propagation**: The ID is passed through every subsequent service call via HTTP headers (e.g., `X-Correlation-ID` or `X-Request-ID`). Each service reads the incoming header, logs with it, and forwards it on outbound calls.

- **Structured Logging**: Each log line includes the correlation ID as a field, enabling log aggregation tools (Datadog, Splunk, ELK) to filter all events for a single request across services in one query.

- **Relationship to OpenTelemetry**: Correlation IDs are a lightweight precursor to full distributed tracing. OpenTelemetry's `traceparent` header extends this concept with span IDs, parent-child relationships, and sampling flags — but a simple correlation ID gets you 80% of the debugging value with minimal setup.

- **Thread-local / Context storage**: Frameworks like Spring (via `MDC`) or Node.js (via `AsyncLocalStorage`) can store the correlation ID so it's automatically included in every log statement without passing it explicitly through every function.

---

## Practical Takeaway / Real-world Gotcha

> **Always generate the ID at the edge, never inside a downstream service.**

If a downstream service generates the ID when it doesn't receive one, you silently lose the upstream context. The fix: enforce ID generation at the gateway and treat a missing `X-Correlation-ID` as a contract violation in internal services.

- Log the correlation ID on **every** log level — not just errors — so you can reconstruct the full request timeline.
- Watch out for **async fire-and-forget calls** that spawn new threads; context propagation libraries don't always cross thread boundaries automatically.
