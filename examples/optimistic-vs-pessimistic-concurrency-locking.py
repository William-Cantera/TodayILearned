"""
Today I Learned Example: Optimistic vs Pessimistic Concurrency Locking
Date: 2026-11-14
"""

# Optimistic vs Pessimistic Concurrency Locking Demo
# =======================================================
# Concurrency control prevents data corruption when multiple threads
# access shared resources simultaneously.
#
# PESSIMISTIC LOCKING: Assumes conflicts WILL happen.
#   - Locks the resource BEFORE reading/writing.
#   - Other threads WAIT until the lock is released.
#   - Best for: high-contention environments, short transactions.
#   - Downside: can cause bottlenecks and deadlocks if misused.
#
# OPTIMISTIC LOCKING: Assumes conflicts are RARE.
#   - Does NOT lock on read; instead uses a version/timestamp check.
#   - On write, verifies nothing changed since the read (compare-and-swap).
#   - If conflict detected, the operation is RETRIED or REJECTED.
#   - Best for: low-contention environments, read-heavy workloads.
#   - Downside: retry overhead when conflicts do occur.

import threading
import time
import random

# ── Shared "database" record ──────────────────────────────────────────────────
record = {"balance": 1000, "version": 0}
record_lock = threading.Lock()          # Used only by pessimistic strategy

# ── PESSIMISTIC LOCKING ───────────────────────────────────────────────────────
pessimistic_conflicts = 0               # Should always be 0 (lock prevents them)

def pessimistic_transfer(amount, thread_id):
    """Acquire the lock first, then read-modify-write safely."""
    global record
    with record_lock:                   # LOCK acquired here — others block
        old_balance = record["balance"]
        time.sleep(random.uniform(0, 0.002))   # Simulate processing delay
        record["balance"] = old_balance + amount
        record["version"] += 1
        # No conflict possible: the lock serialises all access

# ── OPTIMISTIC LOCKING ────────────────────────────────────────────────────────
optimistic_record = {"balance": 1000, "version": 0}
optimistic_lock   = threading.Lock()   # Only used for the atomic commit step
optimistic_conflicts = 0

def optimistic_transfer(amount, thread_id):
    """Read freely, then commit only if version hasn't changed (CAS pattern)."""
    global optimistic_record, optimistic_conflicts
    max_retries = 10
    for attempt in range(max_retries):
        # 1. READ snapshot (no lock held during processing)
        snapshot_balance = optimistic_record["balance"]
        snapshot_version = optimistic_record["version"]

        time.sleep(random.uniform(0, 0.002))   # Simulate processing delay

        # 2. COMMIT: lock briefly only to check-and-swap
        with optimistic_lock:
            if optimistic_record["version"] == snapshot_version:
                # Version unchanged → safe to write
                optimistic_record["balance"] = snapshot_balance + amount
                optimistic_record["version"] += 1
                return  # Success
            else:
                # Version changed by another thread → conflict detected!
                optimistic_conflicts += 1

        # Retry with a small back-off
        time.sleep(random.uniform(0, 0.001))

    print(f"  [Thread-{thread_id}] FAILED after {max_retries} retries!")

# ── Run both strategies with concurrent threads ───────────────────────────────
def run_strategy(strategy_fn, label, expected_balance):
    threads = [
        threading.Thread(target=strategy_fn, args=(random.choice([-50, 100, -30, 75]), i))
        for i in range(20)
    ]
    start = time.perf_counter()
    for t in threads: t.start()
    for t in threads: t.join()
    elapsed = time.perf_counter() - start
    print(f"\n{'='*45}")
    print(f"Strategy : {label}")
    print(f"Final balance (pessimistic) : {record['balance']}")          if label.startswith("Pessimistic") else \
    print(f"Final balance (optimistic)  : {optimistic_record['balance']}")
    print(f"Conflicts detected          : {optimistic_conflicts if label.startswith('Optimistic') else pessimistic_conflicts}")
    print(f"Time elapsed                : {elapsed:.4f}s")
    print(f"{'='*45}")

# Seed random for reproducibility
random.seed(42)

print("Running PESSIMISTIC locking demo...")
run_strategy(pessimistic_transfer, "Pessimistic Locking", None)

print("\nRunning OPTIMISTIC locking demo...")
run_strategy(optimistic_transfer, "Optimistic Locking", None)

# ── Key Takeaways ─
