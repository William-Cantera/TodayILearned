# TIL: Distributed Tracing with Correlation IDs

*Date: 2026-10-31*

## Summary / Problem Statement

When a single user request fans out across multiple microservices, debugging failures becomes a nightmare. Log files from Service A, B, and C each tell a fragment of the story, but without a common thread, correlating those fragments is nearly impossible — especially under load when thousands of requests interleave.

**Distributed tracing with Correlation IDs** solves this by attaching a unique identifier to every request at its origin and propagating it through every downstream call.

---

## Key Concepts & Technical Details

- **Correlation ID**: A unique token (typically a UUID v4) generated at the entry point — usually an API gateway or the first service to receive a request.
- **Propagation**: The ID is forwarded via HTTP headers (e.g., `X-Correlation-ID` or the W3C standard `traceparent`) on every outbound call, including async messages on queues like Kafka or RabbitMQ.
- **Structured Logging**: Each service extracts the ID from the incoming context and injects it into every log entry, enabling a full request timeline with a single log query:
  ```
  { "correlation_id": "a3f9...", "service": "payment-svc", "event": "charge_attempted" }
  ```
- **OpenTelemetry**: The emerging standard that formalizes this pattern with `TraceID` + `SpanID`, allowing tools like Jaeger, Zipkin, or Grafana Tempo to visualize full request traces as waterfall diagrams.
- **Context Propagation Libraries**: Most frameworks handle this automatically — e.g., `opentelemetry-sdk` in Python/Java, or middleware packages in Express/Go.

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha**: Correlation IDs silently disappear at async boundaries.

When a service publishes a message to a queue, developers often forget to embed the Correlation ID in the message payload or headers. The consuming service then starts a brand-new trace, breaking the chain entirely.

**Fix it by:**
- Defining a team-wide contract: the ID **always** travels in message metadata, never just in the HTTP layer.
- Adding automated tests or middleware that assert a Correlation ID is present on every inbound request and outbound message.
- Treating a missing ID as a **first-class bug**, not a minor logging gap.
