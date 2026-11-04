# TIL: Database Connection Pool Exhaustion Mitigation

*Date: 2026-11-03*

## Summary / Problem Statement

Under high traffic, applications can grind to a halt not because the database is slow — but because all available connections in the pool are in use. New requests queue up waiting for a free connection, timeouts cascade, and the whole system appears to be down even though the DB itself is healthy.

## Key Concepts & Technical Details

**What is a connection pool?**
A connection pool maintains a set of pre-established database connections that are reused across requests, avoiding the overhead of creating a new connection on every query.

**How exhaustion happens:**
- Pool size is too small for the incoming request volume
- Connections are held open too long (slow queries, missing `finally` blocks, forgotten transactions)
- N+1 query patterns cause a single request to consume many connections simultaneously
- Microservices each maintain their own pool, multiplying total connections against the DB

**Mitigation strategies:**

- **Right-size your pool** — A common formula: `pool_size = (core_count * 2) + effective_spindle_count`. Bigger isn't always better; too many connections increase DB-side context switching.
- **Set connection timeouts** — Configure both `connect_timeout` and `checkout_timeout` so requests fail fast rather than queue indefinitely.
- **Use a connection pooler** — Tools like **PgBouncer** (PostgreSQL) or **ProxySQL** (MySQL) sit between your app and DB, multiplexing thousands of app connections onto a smaller set of real DB connections.
- **Monitor pool metrics** — Track `pool_checked_out`, `pool_waiting`, and `pool_size` in your APM. Waiting > 0 is your early warning signal.
- **Audit long-running transactions** — A transaction left open by a bug holds a connection hostage. Set `idle_in_transaction_session_timeout` at the DB level as a safety net.

## Practical Takeaway / Real-world Gotcha

> Increasing pool size is rarely the right first fix.

It feels intuitive, but adding more connections often shifts the bottleneck to the database itself. The real fix is almost always **releasing connections faster** — closing them promptly, avoiding long transactions, and offloading connection management to a dedicated pooler. Profile before you tune.
