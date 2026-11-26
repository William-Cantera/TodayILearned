# TIL: Cryptographic Nonce Reuse Vulnerabilities

*Date: 2026-11-25*

## Summary / Problem Statement

Reusing a cryptographic nonce ("number used once") with the same key can catastrophically break the security guarantees of many encryption schemes — often exposing plaintext or allowing message forgery, even without knowing the secret key.

---

## Key Concepts & Technical Details

**What is a nonce?**
- A nonce is a value that must be unique per encryption operation for a given key
- It doesn't need to be secret, but it *must never repeat* under the same key

**Why reuse is fatal — stream cipher example (AES-CTR / ChaCha20):**
- The keystream is generated as: `keystream = Encrypt(key, nonce)`
- Ciphertext is produced via XOR: `C = P ⊕ keystream`
- If two messages share the same key+nonce:
  ```
  C1 = P1 ⊕ keystream
  C2 = P2 ⊕ keystream
  C1 ⊕ C2 = P1 ⊕ P2  ← attacker recovers XOR of plaintexts
  ```
- With known or guessable plaintext, the full message can be recovered

**Authenticated encryption (AES-GCM) is even worse:**
- Nonce reuse in GCM leaks the authentication key (`H`)
- An attacker can **forge arbitrary authenticated messages**, completely breaking integrity
- This is a known attack called *"GCM nonce misuse"*

**Real-world incidents:**
- PS3 was broken partly due to ECDSA nonce reuse — the signing key was fully recovered
- TLS 1.2 implementations have shipped with broken nonce generation for GCM

---

## Practical Takeaway / Real-world Gotcha

- **Never manually manage nonces** unless you have a very good reason — use libraries that handle this automatically (e.g., `libsodium`, Go's `crypto/cipher` with random nonce generation)
- Prefer **nonce-misuse resistant** AEAD schemes like **AES-GCM-SIV** or **XChaCha20-Poly1305**, which tolerate accidental reuse far better
- If you *must* manage nonces, use a **counter with persistent state** or a **random 192-bit nonce** (XChaCha20 makes this safe)
- Treat nonce reuse as a **key compromise** — rotate keys and audit immediately

> 💡 *The rule is simple: one key + one nonce = one message, forever.*
