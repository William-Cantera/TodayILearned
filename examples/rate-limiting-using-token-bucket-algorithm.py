"""
Today I Learned Example: Rate Limiting using Token Bucket Algorithm
Date: 2026-11-22
"""

# Rate Limiting using Token Bucket Algorithm
#
# WHAT IT DOES:
# The Token Bucket algorithm controls the rate at which requests/operations
# are allowed to proceed. Imagine a bucket that holds tokens:
#   - Tokens are added to the bucket at a fixed rate (e.g., 5 tokens/second)
#   - Each request consumes one (or more) tokens
#   - If the bucket has tokens, the request is allowed immediately
#   - If the bucket is empty, the request is denied or must wait
#
# WHEN TO USE IT:
#   - API rate limiting (e.g., allow 100 requests/minute per user)
#   - Network traffic shaping
#   - Controlling access to shared resources (databases, file I/O)
#   - Preventing abuse or denial-of-service scenarios
#
# BEST PRACTICES:
#   - Use threading.Lock() to make the bucket thread-safe
#   - Allow bursting up to bucket capacity (handles traffic spikes gracefully)
#   - Separate buckets per user/client for fair multi-tenant rate limiting
#   - Log or return meaningful feedback when requests are throttled

import time
import threading
import random

class TokenBucket:
    """Thread-safe Token Bucket rate limiter."""

    def __init__(self, capacity: float, refill_rate: float):
        """
        Args:
            capacity:    Maximum number of tokens the bucket can hold (burst limit).
            refill_rate: Number of tokens added per second.
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._tokens = capacity          # Start full so first requests succeed immediately
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()    # Ensures correctness under concurrent access

    def _refill(self):
        """Calculate and add tokens earned since the last refill (called internally)."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        new_tokens = elapsed * self.refill_rate
        # Cap tokens at bucket capacity to prevent unlimited accumulation
        self._tokens = min(self.capacity, self._tokens + new_tokens)
        self._last_refill = now

    def consume(self, tokens: float = 1.0) -> bool:
        """
        Attempt to consume tokens from the bucket.

        Returns:
            True  - request is allowed (tokens were available)
            False - request is denied (bucket is empty / insufficient tokens)
        """
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True             # ✅ Allowed
            return False                # ❌ Throttled

    @property
    def available_tokens(self) -> float:
        with self._lock:
            self._refill()
            return round(self._tokens, 2)


def simulate_requests(bucket: TokenBucket, num_requests: int, label: str):
    """Simulate a burst of requests hitting the rate limiter."""
    allowed = denied = 0
    print(f"\n{'='*50}")
    print(f"[{label}] Sending {num_requests} requests...")
    print(f"{'='*50}")

    for i in range(1, num_requests + 1):
        if bucket.consume():
            allowed += 1
            status = "✅ ALLOWED"
        else:
            denied += 1
            status = "❌ DENIED "

        print(f"  Request {i:>2}: {status}  | Tokens remaining: {bucket.available_tokens}")
        time.sleep(random.uniform(0.05, 0.25))  # Simulate variable request timing

    print(f"\n  Summary → Allowed: {allowed}, Denied: {denied}")


if __name__ == "__main__":
    # --- Demo 1: Burst traffic exceeds bucket capacity ---
    # Bucket holds 5 tokens, refills at 2 tokens/second
    bucket = TokenBucket(capacity=5, refill_rate=2)
    simulate_requests(bucket, num_requests=8, label="Burst Test")

    # --- Demo 2: Steady traffic stays within rate limit ---
    print("\n⏳ Waiting 3 seconds for bucket to refill...")
    time.sleep(3)
    simulate_requests(bucket, num_requests=6, label="Steady Traffic")

    # --- Demo 3: Per-user buckets for fair multi-tenant limiting ---
    print("\n\n--- Per-User Rate Limiting Demo ---")
    users = {uid: TokenBucket(capacity=3, refill_rate=1) for uid in ["alice", "bob"]}
    for _ in range(5):
        for user, b in users.items():
            result = "✅" if b.consume() else "❌"
            print(f"  {user}: {result} (tokens left: {
