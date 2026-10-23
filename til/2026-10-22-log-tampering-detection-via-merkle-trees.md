# TIL: Log Tampering Detection via Merkle Trees

*Date: 2026-10-22*

## Summary / Problem Statement

Logs are only useful as an audit trail if you can trust they haven't been modified. A determined attacker who gains system access can silently edit or delete log entries, erasing evidence of their intrusion. Storing logs in a flat file or even a database offers no built-in integrity guarantee — you need a cryptographic structure to detect tampering.

---

## Key Concepts & Technical Details

**Merkle Trees** provide an efficient way to verify the integrity of a sequence of log entries without re-hashing the entire dataset.

- **Structure:** Each log entry is hashed individually (leaf nodes). Pairs of hashes are then combined and hashed again, propagating up until a single **Merkle Root** is produced.
- **Tamper Evidence:** Changing *any* single log entry changes its leaf hash, which cascades upward and produces a different root. Comparing the stored root against a recomputed one immediately reveals tampering.
- **Efficiency:** Verifying a single entry only requires `O(log n)` hashes (the sibling path from leaf to root), not the full dataset.
- **Append-Only Logs:** Systems like **Certificate Transparency** and **Trillian** use Merkle trees to build append-only, publicly auditable logs. New entries extend the tree; they cannot be silently inserted or removed.
- **Consistency Proofs:** A Merkle tree can also prove that an older root is a valid prefix of a newer one — confirming no historical entries were rewritten between snapshots.

**Common hash functions used:** SHA-256 is standard; avoid MD5/SHA-1 for security-critical logs.

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** Storing the Merkle root in the *same system* as the logs defeats the purpose. An attacker with write access can recompute and overwrite the root after altering entries.

- **Best practice:** Publish or escrow the root hash externally — a separate write-once store, a blockchain anchor, or a signed timestamp service.
- **Operational tip:** Log rotation breaks naive implementations. Design your tree to handle epoch boundaries explicitly, or use a persistent tree structure like a **history tree**.
- Even a simple periodic root hash published to an immutable external endpoint dramatically raises the cost of undetected log manipulation.
