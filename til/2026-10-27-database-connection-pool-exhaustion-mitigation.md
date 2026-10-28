# TIL: Database Connection Pool Exhaustion Mitigation

*Date: 2026-10-27*

## Summary / Problem Statement

Under high load, applications can exhaust their database connection pool — meaning every available connection is in use and new requests are forced to wait or fail outright. This manifests as timeout errors, cascading failures, and degraded user experience, even when the database itself is perfectly healthy.

---

## Key Concepts & Technical Details

**What is a connection pool?**
A connection pool maintains a fixed set of pre-established database connections that are borrowed and returned by application threads, avoiding the overhead of creating a new connection on every request.

**Why exhaustion happens:**
- Pool size is too small for the concurrency level
- Connections are held too long (slow queries, missing `finally` blocks, ORM session mismanagement)
- External services cause request threads to stall while holding a connection
- N+1 query patterns amplify connection hold time

**Mitigation strategies:**

- **Right-size your pool** — A common starting formula is `pool_size = (core_count * 2) + effective_spindle_count`. Avoid setting it arbitrarily high; larger pools increase database-side memory pressure.
- **Set connection timeouts** — Configure both `connect_timeout` and `checkout_timeout` so threads fail fast rather than pile up.
- **Use a connection proxy / pgBouncer** — Tools like PgBouncer (PostgreSQL) or ProxySQL (MySQL) multiplex thousands of app connections onto a smaller set of real server connections.
- **Monitor pool metrics** — Track `pool.checked_out`, `pool.overflow`, and `pool.wait_time`. Alert before exhaustion, not after.
- **Audit long-running transactions** — Queries holding connections open for seconds are a red flag; enforce query timeouts at the driver level.
- **Async/non-blocking I/O** — Frameworks like asyncpg or HikariCP's async borrowing reduce per-request connection hold time significantly.

---

## Practical Takeaway / Real-world Gotcha

> Increasing pool size is almost never the right first fix.

A pool size of 100 with slow queries will exhaust faster than a pool of 20 with fast ones. The real culprit is usually **connection hold time**, not pool count. Always profile query duration and check for unreleased connections before tuning pool limits — otherwise you're just delaying the inevitable while adding load to your database server.
