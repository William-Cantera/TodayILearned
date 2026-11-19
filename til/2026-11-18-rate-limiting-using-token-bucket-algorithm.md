# TIL: Rate Limiting using Token Bucket Algorithm

*Date: 2026-11-18*

## Summary / Problem Statement

When building APIs or distributed services, uncontrolled traffic can overwhelm your system — causing cascading failures or degraded performance. Rate limiting is the go-to solution, and the **Token Bucket Algorithm** is one of the most elegant and widely-used approaches to implement it.

The core challenge: how do you allow short bursts of traffic while still enforcing a sustained rate limit over time?

---

## Key Concepts & Technical Details

The token bucket works like a literal bucket that holds tokens:

- **Tokens are added** to the bucket at a fixed rate (e.g., 10 tokens/second)
- **Each incoming request consumes** one (or more) tokens
- If the bucket **has tokens**, the request is allowed through
- If the bucket is **empty**, the request is rejected or queued
- The bucket has a **maximum capacity** — tokens beyond the cap are discarded

**Key parameters:**
- `capacity` — maximum burst size the bucket can hold
- `refill_rate` — how many tokens are added per unit time
- `current_tokens` — the live count checked on each request

**Pseudocode sketch:**
```
on each request:
  refill tokens based on elapsed time
  if current_tokens >= cost:
    current_tokens -= cost
    allow request
  else:
    reject / return 429
```

**Why it handles bursts well:**
A full bucket lets a sudden spike consume up to `capacity` requests immediately, while the `refill_rate` enforces the long-term average — giving you both flexibility and control.

---

## Practical Takeaway / Real-world Gotcha

- **Distributed systems gotcha:** A single in-memory bucket doesn't work across multiple server instances. You need a shared store (e.g., Redis with atomic Lua scripts) to keep token counts consistent.
- **Clock drift matters:** Token refill is time-based, so inaccurate or inconsistent clocks across nodes can cause subtle over- or under-limiting.
- **Cost-per-request:** Expensive endpoints (e.g., bulk exports) can deduct *multiple* tokens per call, giving you fine-grained throttling beyond simple request counts.
- Libraries like **`redis-cell`** or **Nginx's `limit_req`** implement this out of the box — prefer battle-tested solutions before rolling your own.
