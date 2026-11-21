# TIL: Database Connection Pool Exhaustion Mitigation

*Date: 2026-11-20*

## Summary / Problem Statement

Connection pool exhaustion occurs when all available database connections in a pool are in use and new requests are forced to wait — or fail outright. This is a silent killer in production systems: the app appears healthy, but latency spikes and timeouts cascade rapidly under load.

---

## Key Concepts & Technical Details

**What is a connection pool?**
A pool maintains a set of reusable database connections, avoiding the overhead of opening/closing a connection per query. Libraries like HikariCP, pgBouncer, and SQLAlchemy manage this automatically.

**Why exhaustion happens:**
- Pool size is too small for concurrent request volume
- Connections are held open too long (slow queries, missing `finally` blocks, unreleased transactions)
- Connection leaks — code acquires a connection and never returns it
- Thundering herd — sudden traffic spike overwhelms a conservatively sized pool

**Key configuration knobs:**
- `maxPoolSize` — maximum concurrent connections allowed
- `connectionTimeout` — how long a thread waits before throwing an error
- `idleTimeout` — how long an idle connection is kept before being released
- `maxLifetime` — forces connection recycling to prevent stale connections

**Detection signals:**
- Metrics: `pool.pending_threads`, `pool.active_connections` near ceiling
- Logs: `Connection is not available, request timed out after Xms`
- Slow query logs showing queries that never started (wait time, not execution time)

**Mitigation strategies:**
- Right-size the pool: `connections = (core_count * 2) + effective_spindle_count` (HikariCP's formula)
- Use a connection proxy like **pgBouncer** in transaction mode to multiplex thousands of app connections onto fewer DB connections
- Enforce query timeouts at the statement level, not just the pool level
- Audit for connection leaks using tools like `leak-detection-threshold` in HikariCP

---

## Practical Takeaway / Real-world Gotcha

> Increasing `maxPoolSize` is tempting but often counterproductive — databases have their own connection limits, and too many connections cause context-switching overhead that *slows* throughput.

The real fix is usually **releasing connections faster**, not acquiring more of them. Always audit transaction scope and ensure connections are returned in all code paths, especially error branches.
