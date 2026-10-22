# TIL: Optimistic vs Pessimistic Concurrency Locking

*Date: 2026-10-21*

## Summary / Problem Statement

When multiple users or processes try to read and update the same data simultaneously, you risk **lost updates** and **data corruption**. Two classic strategies handle this: **optimistic** and **pessimistic** concurrency control. Choosing the wrong one for your workload can cause silent data loss or crippling database contention.

---

## Key Concepts & Technical Details

### Pessimistic Locking
- **Assumes conflict is likely** — locks the resource before reading it.
- Uses database-level locks: `SELECT ... FOR UPDATE` in SQL.
- Other transactions **block and wait** until the lock is released.
- Safe for high-contention scenarios (e.g., booking seats, financial ledgers).
- Risk: **deadlocks** if two transactions lock resources in opposite orders.

### Optimistic Locking
- **Assumes conflict is rare** — reads data freely, checks for conflict only at write time.
- Typically implemented with a **version column** (`version`, `updated_at`, or ETag).
- On update, the query checks: `WHERE id = ? AND version = ?`
  - If rows affected = `0`, someone else modified it → **raise a conflict error and retry**.
- No locks held during the transaction; great for **read-heavy, low-contention** workloads.
- Risk: **retry storms** under high contention — many transactions fail and retry simultaneously.

### Quick Comparison

| | Pessimistic | Optimistic |
|---|---|---|
| Lock held? | Yes, upfront | No |
| Best for | High contention | Low contention |
| Failure mode | Deadlocks | Retry storms |
| Throughput | Lower | Higher |

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** Optimistic locking silently does nothing if you forget to check the affected row count after your `UPDATE`. The query succeeds with `0` rows updated, your application never raises an error, and the conflicting write is **silently dropped**.

- Always assert `rowsAffected === 1` after an optimistic update.
- Use **pessimistic locking** for anything financial or inventory-related where correctness beats throughput.
- In ORMs (Hibernate, SQLAlchemy, ActiveRecord), enable versioning explicitly — it's rarely on by default.
