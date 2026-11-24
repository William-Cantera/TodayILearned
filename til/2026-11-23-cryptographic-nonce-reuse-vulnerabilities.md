# TIL: Cryptographic Nonce Reuse Vulnerabilities

*Date: 2026-11-23*

## Summary / Problem Statement

Reusing a cryptographic nonce ("number used once") with the same key can completely break the confidentiality — and sometimes integrity — of an encryption scheme. This is one of those mistakes that looks harmless on the surface but has catastrophic consequences in practice.

---

## Key Concepts & Technical Details

**What is a nonce?**
- A nonce is a value that must be unique per encryption operation for a given key
- Common in stream ciphers, CTR mode, GCM mode, and authenticated encryption schemes (AEAD)

**Why reuse is fatal — the keystream attack:**
- In stream ciphers and CTR mode, a unique nonce generates a unique *keystream*
- Encryption is simply: `ciphertext = plaintext XOR keystream`
- If you reuse a nonce with the same key, both messages share the **same keystream**
- An attacker who intercepts both ciphertexts can compute:
  ```
  C1 XOR C2 = (P1 XOR KS) XOR (P2 XOR KS) = P1 XOR P2
  ```
- With enough known or guessable plaintext, the attacker can recover both messages entirely

**AES-GCM nonce reuse is even worse:**
- Reusing a nonce in AES-GCM doesn't just leak plaintext — it **exposes the authentication key (H)**
- Once H is known, an attacker can forge valid authentication tags for arbitrary ciphertexts
- This breaks both *confidentiality* and *integrity* simultaneously

**Real-world examples:**
- The PS3 private key leak (2010) — Sony reused a nonce in ECDSA signing, allowing private key recovery
- TLS 1.2 implementations with poor IV management in CBC/GCM modes
- Embedded systems with non-random RNGs generating repeated nonces

---

## Practical Takeaway / Real-world Gotcha

- **Never manually manage nonces** if the library can do it for you — use APIs that auto-generate them (e.g., `crypto/rand` in Go, `secrets` in Python)
- Prefer **nonce-misuse resistant** schemes like **AES-GCM-SIV** or **XChaCha20-Poly1305** which tolerate accidental reuse more gracefully
- In distributed systems, coordinate nonce generation carefully — concurrent processes are a common source of collisions
- Treat nonce generation with the same seriousness as key management
