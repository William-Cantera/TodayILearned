# TIL: Distributed Tracing with Correlation IDs

*Date: 2026-10-25*

## Summary / Problem Statement

When a single user request flows through multiple microservices, debugging failures becomes a nightmare. Logs from Service A, Service B, and Service C exist in isolation — there's no native way to stitch them together into a coherent timeline. Distributed tracing with **Correlation IDs** solves this by threading a unique identifier through every hop in the request chain.

---

## Key Concepts & Technical Details

**What is a Correlation ID?**
- A unique identifier (typically a UUID v4) generated at the **entry point** of a request — usually an API gateway or the first service in the chain.
- Propagated downstream via HTTP headers (e.g., `X-Correlation-ID` or `X-Request-ID`).

**How propagation works:**
1. Gateway receives a request → generates `correlationId = uuid()` if none exists.
2. Every outbound HTTP call, message queue publish, or gRPC request **forwards the same header**.
3. Each service **logs the correlationId** alongside every log line for that request.
4. To query the full trace: `grep` or filter logs by that single ID across all services.

**Integration with structured logging:**
```json
{
  "timestamp": "2024-11-01T10:22:31Z",
  "level": "INFO",
  "service": "order-service",
  "correlationId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "message": "Order created successfully"
}
```

**Relation to OpenTelemetry:**
- Correlation IDs are a lightweight, DIY form of what tools like **Jaeger**, **Zipkin**, and **OpenTelemetry** formalize as `traceId` + `spanId`.
- They're not mutually exclusive — many teams use both.

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** If any service in the chain *forgets* to forward the header, the trace silently breaks. You'll see partial logs and assume the request stopped there — when it actually continued untraced.

**Defensive practices:**
- Use **middleware/interceptors** at the framework level so propagation is automatic, not manual.
- Accept an *incoming* Correlation ID if one already exists (e.g., from a client or upstream partner) rather than always generating a new one — this preserves end-to-end traceability across system boundaries.
- Treat a missing `X-Correlation-ID` in internal service calls as a **code smell** worth linting or alerting on.
