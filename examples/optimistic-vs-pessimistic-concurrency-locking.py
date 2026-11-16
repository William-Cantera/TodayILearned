"""
Today I Learned Example: Optimistic vs Pessimistic Concurrency Locking
Date: 2026-11-15
"""

# Optimistic vs Pessimistic Concurrency Locking Demo
# =======================================================
# Concurrency control strategies prevent data corruption when multiple
# threads/processes access shared resources simultaneously.
#
# PESSIMISTIC LOCKING: Assumes conflicts WILL happen.
#   - Acquires a lock BEFORE reading data, holds it until write completes.
#   - Best for: high-contention environments, long transactions, write-heavy workloads.
#   - Drawback: reduces throughput; threads block waiting for locks.
#
# OPTIMISTIC LOCKING: Assumes conflicts are RARE.
#   - No lock on read; uses a version/timestamp to detect conflicts at write time.
#   - Best for: low-contention environments, read-heavy workloads, short transactions.
#   - Drawback: requires retry logic; wasteful if conflicts are frequent.

import threading
import time
import random

# ---------------------------------------------------------------------------
# Shared "database" record — a simple dict simulating a DB row
# ---------------------------------------------------------------------------
record = {"value": 100, "version": 0}
record_lock = threading.Lock()  # Used only by pessimistic approach

# ---------------------------------------------------------------------------
# PESSIMISTIC LOCKING IMPLEMENTATION
# Best practice: keep the critical section as SHORT as possible.
# ---------------------------------------------------------------------------
def pessimistic_update(thread_id, amount):
    """Acquire lock first, then read-modify-write. No conflict possible."""
    print(f"[Pessimistic] Thread-{thread_id}: waiting for lock...")
    with record_lock:                          # Block until lock is acquired
        # Simulate some processing time inside the lock (keep this minimal!)
        time.sleep(random.uniform(0.01, 0.05))
        old_value = record["value"]
        record["value"] += amount
        record["version"] += 1
        print(f"[Pessimistic] Thread-{thread_id}: "
              f"{old_value} -> {record['value']} (v{record['version']})")

# ---------------------------------------------------------------------------
# OPTIMISTIC LOCKING IMPLEMENTATION
# Best practice: retry on conflict; use exponential back-off in production.
# ---------------------------------------------------------------------------
def optimistic_update(thread_id, amount, max_retries=5):
    """Read freely, then validate version before committing the write."""
    for attempt in range(1, max_retries + 1):
        # --- READ PHASE (no lock) ---
        snapshot_value   = record["value"]     # Read current value
        snapshot_version = record["version"]   # Remember the version we saw

        # Simulate processing / business logic outside any lock
        time.sleep(random.uniform(0.01, 0.05))
        new_value = snapshot_value + amount

        # --- WRITE PHASE (short lock only to check-and-set) ---
        with record_lock:
            if record["version"] == snapshot_version:   # No one changed it?
                record["value"]   = new_value           # Safe to commit
                record["version"] += 1
                print(f"[Optimistic]  Thread-{thread_id}: attempt {attempt} "
                      f"SUCCESS  {snapshot_value} -> {record['value']} "
                      f"(v{record['version']})")
                return  # Done — exit retry loop
            else:
                # Another thread changed the record; our snapshot is stale
                print(f"[Optimistic]  Thread-{thread_id}: attempt {attempt} "
                      f"CONFLICT — retrying...")

    print(f"[Optimistic]  Thread-{thread_id}: gave up after {max_retries} retries!")

# ---------------------------------------------------------------------------
# DEMO: run both strategies sequentially so output is readable
# ---------------------------------------------------------------------------
def run_demo(strategy_fn, label, num_threads=4):
    global record
    record = {"value": 100, "version": 0}      # Reset shared state
    print(f"\n{'='*55}")
    print(f"  {label}  (starting value = {record['value']})")
    print(f"{'='*55}")

    threads = [
        threading.Thread(target=strategy_fn, args=(i, random.choice([-10, 10, 20])))
        for i in range(1, num_threads + 1)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"\n  Final record: value={record['value']}, version={record['version']}")

if __name__ == "__main__":
    random.seed(42)
    run_demo(pessimistic_update, "PESSIMISTIC LOCKING")
    run_demo(optimistic_update,  "OPTIMISTIC LOCKING")

    print("\n--- Key Takeaways ---")
    print("Pessimistic: zero retries, but threads queue up  → use for high contention.")
    print("Optimistic :
