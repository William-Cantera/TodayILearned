# TIL: Distributed Tracing with Correlation IDs

*Date: 2026-10-24*

## Summary / Problem Statement

When a single user request fans out across multiple microservices, debugging failures becomes a nightmare. Log files from Service A, Service B, and Service C each tell a fragment of the story — but without a way to stitch them together, you're hunting for a needle in several haystacks simultaneously.

**Distributed tracing with Correlation IDs** solves this by attaching a unique identifier to every request at its entry point and propagating it through every downstream call.

---

## Key Concepts & Technical Details

- **Correlation ID**: A UUID (e.g., `4b3f9a12-...`) generated at the edge — typically in an API gateway or the first service that receives the request.
- **Propagation**: The ID is forwarded via HTTP headers (commonly `X-Correlation-ID` or the W3C standard `traceparent`) on every outbound call the service makes.
- **Structured Logging**: Each service includes the correlation ID in every log line it emits for that request, making cross-service log queries trivial.
- **Spans & Traces**: Tools like **OpenTelemetry**, **Jaeger**, or **Zipkin** build on this concept. A *trace* is the full end-to-end journey; a *span* is one service's slice of that journey. The correlation ID maps to a `trace_id`.
- **Context Propagation Libraries**: OpenTelemetry SDKs handle header injection/extraction automatically, so you don't manually thread the ID through every function call.

```http
GET /orders/42 HTTP/1.1
X-Correlation-ID: 4b3f9a12-8c1e-4d77-b3a0-9f2e1c305d88
```

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha**: Async boundaries silently drop context.

When a service publishes a message to a queue (Kafka, RabbitMQ, SQS), the correlation ID lives in HTTP headers — which don't exist on a message by default. You **must** explicitly serialize the ID into the message payload or metadata headers, then deserialize and re-attach it in the consumer.

- ✅ Always treat message brokers as a propagation boundary requiring manual handling.
- ✅ Log the correlation ID at the very start of every consumer handler.
- ✅ Adopt OpenTelemetry early — retrofitting tracing into a mature system is painful.
