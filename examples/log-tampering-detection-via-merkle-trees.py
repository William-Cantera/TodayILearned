"""
Today I Learned Example: Log Tampering Detection via Merkle Trees
Date: 2026-11-06
"""

# Log Tampering Detection via Merkle Trees
#
# WHAT: A Merkle tree is a binary hash tree where each leaf node contains the hash
# of a log entry, and each parent node contains the hash of its children's hashes.
# The root hash (Merkle root) acts as a cryptographic fingerprint of ALL log entries.
#
# WHY/WHEN TO USE:
#   - Detect if any log entry has been silently modified, deleted, or inserted
#   - Audit trails for financial systems, security logs, compliance records
#   - Efficient tamper detection: only O(log n) hashes needed to verify one entry
#
# BEST PRACTICES:
#   - Store the Merkle root separately from the logs (different server/medium)
#   - Periodically snapshot and sign the root with a private key (not shown here)
#   - Use SHA-256 or stronger; never MD5/SHA-1 for security-critical logs
#   - Re-hash with a nonce or timestamp to prevent length-extension attacks

import hashlib
import copy

def hash_entry(data: str) -> str:
    """Hash a single log entry string using SHA-256."""
    return hashlib.sha256(data.encode()).hexdigest()

def hash_pair(left: str, right: str) -> str:
    """Combine two hashes into a parent hash (concatenate then hash)."""
    return hashlib.sha256((left + right).encode()).hexdigest()

def build_merkle_tree(entries: list) -> list:
    """
    Build a Merkle tree from a list of log entry strings.
    Returns a list of levels: level[0] = leaf hashes, level[-1] = [root].
    If the number of nodes at a level is odd, duplicate the last node
    (standard Merkle tree convention).
    """
    if not entries:
        return []

    # Level 0: hash each log entry
    current_level = [hash_entry(e) for e in entries]
    tree = [current_level]

    while len(current_level) > 1:
        next_level = []
        # Duplicate last element if odd number of nodes
        if len(current_level) % 2 == 1:
            current_level.append(current_level[-1])
        for i in range(0, len(current_level), 2):
            next_level.append(hash_pair(current_level[i], current_level[i + 1]))
        tree.append(next_level)
        current_level = next_level

    return tree

def get_merkle_root(tree: list) -> str:
    """Return the Merkle root (top-level single hash)."""
    return tree[-1][0] if tree else ""

def verify_integrity(original_root: str, current_logs: list) -> bool:
    """Rebuild the tree from current logs and compare root to the stored root."""
    new_tree = build_merkle_tree(current_logs)
    new_root = get_merkle_root(new_tree)
    return new_root == original_root

# ── DEMO ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Simulate an application log
    logs = [
        "2024-01-10 08:00:01 INFO  User 'alice' logged in",
        "2024-01-10 08:05:33 INFO  User 'alice' accessed /reports",
        "2024-01-10 08:07:12 WARN  Failed login attempt for 'bob'",
        "2024-01-10 08:10:55 INFO  User 'carol' logged in",
        "2024-01-10 08:15:00 ERROR Database connection timeout",
    ]

    # Build the original Merkle tree and store the root securely
    tree = build_merkle_tree(logs)
    original_root = get_merkle_root(tree)
    print(f"[ORIGINAL] Merkle root: {original_root}\n")

    # ── Scenario 1: No tampering ──────────────────────────────────────────────
    intact_logs = copy.deepcopy(logs)
    result = verify_integrity(original_root, intact_logs)
    print(f"Scenario 1 – Logs unchanged:          Integrity OK? {result}")

    # ── Scenario 2: An attacker modifies one log entry ────────────────────────
    tampered_logs = copy.deepcopy(logs)
    tampered_logs[2] = "2024-01-10 08:07:12 INFO  User 'bob' logged in"  # erased WARN
    result = verify_integrity(original_root, tampered_logs)
    print(f"Scenario 2 – One entry modified:      Integrity OK? {result}")

    # ──
