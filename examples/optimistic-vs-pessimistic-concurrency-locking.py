"""
Today I Learned Example: Optimistic vs Pessimistic Concurrency Locking
Date: 2026-11-15
"""

# Optimistic vs Pessimistic Concurrency Locking Demo
# =====================================================
# Concurrency control prevents data corruption when multiple threads
# access shared resources simultaneously.
#
# PESSIMISTIC LOCKING: Assumes conflicts WILL happen.
#   - Locks the resource BEFORE reading/writing.
#   - Other threads BLOCK until the lock is released.
#   - Best for: High-contention environments, short transactions.
#
# OPTIMISTIC LOCKING: Assumes conflicts are RARE.
#   - No lock on read; uses a VERSION NUMBER to detect conflicts.
#   - On write, checks if version changed since last read.
#   - If version mismatch → conflict detected → retry or abort.
#   - Best for: Low-contention environments, long read operations.

import threading
import time
import random

# ── Shared "database" record ──────────────────────────────────────────────────

class BankAccount:
    """Simulates a database row with a version field for optimistic locking."""
    def __init__(self, balance: int):
        self.balance  = balance
        self.version  = 0          # Incremented on every successful write
        self._lock    = threading.Lock()   # Used only by pessimistic strategy

# ── PESSIMISTIC LOCKING ───────────────────────────────────────────────────────

def pessimistic_deposit(account: BankAccount, amount: int, thread_name: str):
    """
    Acquire the lock FIRST, then read-modify-write.
    Guarantees no other thread can interfere during the entire operation.
    Downside: threads queue up, reducing throughput under heavy load.
    """
    with account._lock:                      # Block until lock is acquired
        old_balance = account.balance
        time.sleep(random.uniform(0, 0.02))  # Simulate processing delay
        account.balance += amount
        account.version += 1
        print(f"  [PESSIMISTIC] {thread_name}: "
              f"{old_balance} → {account.balance}  (v{account.version})")

# ── OPTIMISTIC LOCKING ────────────────────────────────────────────────────────

def optimistic_deposit(account: BankAccount, amount: int, thread_name: str):
    """
    Read WITHOUT locking, then attempt a conditional write.
    If the version changed between read and write → conflict → retry.
    Downside: wasted work on conflict; bad under heavy contention.
    """
    retries = 0
    while True:
        # 1. Snapshot the current state (no lock needed for the read)
        read_version = account.version
        old_balance  = account.balance
        new_balance  = old_balance + amount

        time.sleep(random.uniform(0, 0.02))  # Simulate processing delay

        # 2. Commit phase: use a brief lock ONLY to check-and-swap atomically
        with account._lock:
            if account.version == read_version:      # No conflict → commit
                account.balance = new_balance
                account.version += 1
                print(f"  [OPTIMISTIC]  {thread_name}: "
                      f"{old_balance} → {account.balance}  "
                      f"(v{account.version}, retries={retries})")
                return
            else:                                    # Conflict → retry
                retries += 1
                print(f"  [OPTIMISTIC]  {thread_name}: "
                      f"CONFLICT (expected v{read_version}, "
                      f"found v{account.version}) — retrying…")

# ── RUNNER ────────────────────────────────────────────────────────────────────

def run_demo(strategy_fn, label: str):
    account   = BankAccount(balance=1000)
    expected  = account.balance + 5 * 100   # 5 threads each deposit 100
    print(f"\n{'─'*55}\n{label}\nStarting balance: {account.balance}\n{'─'*55}")

    threads = [
        threading.Thread(target=strategy_fn,
                         args=(account, 100, f"Thread-{i+1}"))
        for i in range(5)
    ]
    for t in threads: t.start()
    for t in threads: t.join()

    status = "✓ CORRECT" if account.balance == expected else "✗ WRONG"
    print(f"{'─'*55}")
    print(f"Final balance : {account.balance}  (expected {expected})  {status}")

# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Best practice: choose the strategy based on your contention profile.
    # Both strategies below should yield the correct final balance (1500
