# TIL: Optimistic vs Pessimistic Concurrency Locking

*Date: 2026-11-26*

## Summary / Problem Statement

When multiple users or processes try to read and update the same data simultaneously, you risk **lost updates** and **data corruption**. Two fundamental strategies exist for handling this: **optimistic** and **pessimistic** concurrency control. Choosing the wrong one for your workload can tank performance or silently corrupt data.

---

## Key Concepts & Technical Details

### Pessimistic Locking
Assumes conflicts **will** happen, so it locks the resource upfront.

- Acquires a database lock (e.g., `SELECT ... FOR UPDATE`) before reading
- Other transactions **block** until the lock is released
- Safe for high-contention scenarios (e.g., inventory deduction, bank transfers)
- Risk: **deadlocks** if two transactions lock resources in opposite orders
- Higher overhead due to lock management

```sql
-- PostgreSQL example
BEGIN;
SELECT balance FROM accounts WHERE id = 42 FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE id = 42;
COMMIT;
```

### Optimistic Locking
Assumes conflicts are **rare**, so it skips locking and validates at write time.

- Reads data freely, then checks a **version number** or **timestamp** before committing
- If the version changed since the read, the transaction is **rejected and retried**
- Common in ORMs (e.g., Hibernate `@Version`, Rails `lock_version`)
- Risk: **high retry storms** under contention

```sql
-- Check version before updating
UPDATE products SET stock = 9, version = 6
WHERE id = 1 AND version = 5;
-- 0 rows affected? Someone else updated first — retry!
```

---

## Practical Takeaway / Real-world Gotcha

> **Match the strategy to your contention profile.**

- Use **pessimistic** locking when conflicts are frequent and the cost of retrying is high (financial transactions, seat reservations)
- Use **optimistic** locking when reads vastly outnumber writes and conflicts are rare (user profile updates, CMS edits)

⚠️ **Gotcha:** Optimistic locking in a high-traffic flash sale can cause a **retry avalanche** — hundreds of threads hammering the database simultaneously. In that scenario, pessimistic locking or a queue-based approach is far safer despite the added overhead.
