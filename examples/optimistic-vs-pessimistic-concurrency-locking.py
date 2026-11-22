"""
Today I Learned Example: Optimistic vs Pessimistic Concurrency Locking
Date: 2026-11-21
"""

# Optimistic vs Pessimistic Concurrency Locking Demo
# =======================================================
# Concurrency control prevents data corruption when multiple threads/processes
# access shared resources simultaneously.
#
# PESSIMISTIC LOCKING: Assumes conflicts WILL happen. Locks the resource before
# reading/writing. Safe but can cause bottlenecks. Best for high-contention
# environments (e.g., bank transactions, inventory systems).
#
# OPTIMISTIC LOCKING: Assumes conflicts are RARE. No lock on read; validates
# version/timestamp before writing. Retries on conflict. Best for low-contention
# environments (e.g., user profile updates, CMS edits).

import threading
import time
import random

# ─── Shared "Database" Records ───────────────────────────────────────────────

pessimistic_record = {"balance": 1000, "lock": threading.Lock()}

optimistic_record  = {"balance": 1000, "version": 0}
optimistic_lock    = threading.Lock()   # Only used during the tiny commit window

# ─── PESSIMISTIC LOCKING ─────────────────────────────────────────────────────

def pessimistic_withdraw(thread_id, amount):
    """
    Acquire the lock BEFORE reading. No other thread can touch the record
    until we release it. Guarantees consistency; may cause waiting.
    """
    print(f"[Pessimistic] Thread-{thread_id} waiting for lock...")
    with pessimistic_record["lock"]:          # Block here until lock is free
        print(f"[Pessimistic] Thread-{thread_id} acquired lock.")
        balance = pessimistic_record["balance"]
        time.sleep(random.uniform(0.05, 0.15))  # Simulate DB read/processing delay

        if balance >= amount:
            pessimistic_record["balance"] = balance - amount
            print(f"[Pessimistic] Thread-{thread_id} withdrew ${amount}. "
                  f"Balance: ${pessimistic_record['balance']}")
        else:
            print(f"[Pessimistic] Thread-{thread_id} insufficient funds.")
    # Lock released automatically here — other threads can now proceed

# ─── OPTIMISTIC LOCKING ──────────────────────────────────────────────────────

def optimistic_withdraw(thread_id, amount):
    """
    Read WITHOUT locking. Before writing, check if version matches what we
    read. If another thread changed it first, RETRY. No blocking on reads.
    """
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        # STEP 1: Read current state (no lock needed)
        balance = optimistic_record["balance"]
        version = optimistic_record["version"]
        print(f"[Optimistic]  Thread-{thread_id} read balance=${balance} "
              f"(version={version}, attempt={attempt})")

        time.sleep(random.uniform(0.05, 0.15))  # Simulate processing delay

        # STEP 2: Attempt to commit — lock only for the brief version check+write
        with optimistic_lock:
            if optimistic_record["version"] != version:
                # Conflict detected! Another thread committed while we worked.
                print(f"[Optimistic]  Thread-{thread_id} CONFLICT — retrying...")
                continue                        # Retry the whole operation

            # No conflict: safe to write
            if balance >= amount:
                optimistic_record["balance"] -= amount
                optimistic_record["version"] += 1   # Increment version on every write
                print(f"[Optimistic]  Thread-{thread_id} withdrew ${amount}. "
                      f"Balance: ${optimistic_record['balance']} "
                      f"(version={optimistic_record['version']})")
            else:
                print(f"[Optimistic]  Thread-{thread_id} insufficient funds.")
            return  # Success (or legitimate failure) — exit retry loop

    print(f"[Optimistic]  Thread-{thread_id} gave up after {max_retries} retries.")

# ─── Run Both Demos ──────────────────────────────────────────────────────────

def run_demo(label, target_fn, withdraw_amount):
    print(f"\n{'='*55}")
    print(f"  {label}")
    print(f"{'='*55}")
    threads = [threading.Thread(target=target_fn, args=(i, withdraw_amount))
               for i in range(1, 5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

run_demo("PESSIMISTIC LOCKING  (4 threads, $200 each)",
         pessimistic_withdraw, 200)

run_demo("OPTIMISTIC
