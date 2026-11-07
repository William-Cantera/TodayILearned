# TIL: Distributed Tracing with Correlation IDs

*Date: 2026-11-06*

## Summary / Problem Statement

When a single user request fans out across multiple microservices, pinpointing where a failure or latency spike occurred becomes extremely difficult. Log lines from different services have no shared context, making it nearly impossible to reconstruct the full request journey without **correlation IDs** and distributed tracing.

---

## Key Concepts & Technical Details

**Correlation ID**
- A unique identifier (typically a UUID v4) generated at the **entry point** of a request — usually an API gateway or the first service to receive it.
- Propagated through every downstream service call via HTTP headers (e.g., `X-Correlation-ID` or `X-Request-ID`).
- Every service logs this ID alongside its own output, enabling full log aggregation across services.

**Distributed Tracing**
- Builds on correlation IDs by adding **spans** — individual units of work with start/end timestamps and metadata.
- A **trace** is the complete tree of spans for one request lifecycle.
- Standards like **OpenTelemetry** define how context is propagated (via the `traceparent` W3C header), keeping instrumentation vendor-neutral.
- Common backends: Jaeger, Zipkin, AWS X-Ray, Honeycomb.

**Context Propagation**
- Must be explicit in async workflows (message queues, event streams). When publishing to Kafka or SQS, the correlation ID must be embedded in the **message headers or payload**, not just the HTTP layer.
- Thread-local storage or async context managers (e.g., Python's `contextvars`, Java's `MDC`) carry the ID without polluting every function signature.

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** Async boundaries silently drop trace context.

A common mistake is assuming correlation IDs flow automatically into background jobs or message consumers. They don't — you must **explicitly extract and re-inject** the ID when crossing async boundaries.

- ✅ Always include the correlation ID in queue message metadata.
- ✅ Log it at the **start** of every service handler, not just on errors.
- ✅ Return the correlation ID to the client in the response header — it makes support debugging dramatically faster.
- ❌ Don't generate a new ID mid-chain; that breaks the trace linkage entirely.
