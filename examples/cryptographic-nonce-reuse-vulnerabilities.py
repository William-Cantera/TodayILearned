"""
Today I Learned Example: Cryptographic Nonce Reuse Vulnerabilities
Date: 2026-11-13
"""

# Cryptographic Nonce Reuse Vulnerabilities
# This script demonstrates why reusing a nonce (number used once) in stream ciphers
# is catastrophic. We simulate a simplified XOR-based stream cipher (similar to how
# CTR mode or OTP works) to show how nonce reuse leaks plaintext.
#
# WHEN THIS MATTERS: Any stream cipher (AES-CTR, ChaCha20, RC4, OTP) where the same
# keystream must NEVER be used twice. Nonce reuse allows an attacker to XOR two
# ciphertexts together and cancel out the key, recovering plaintext relationships.
#
# BEST PRACTICES:
# - Use a random nonce for every encryption operation
# - Use authenticated encryption (AES-GCM) which detects tampering
# - Never reuse a (key, nonce) pair under any circumstances
# - Prefer nonce-misuse resistant schemes (AES-SIV) for critical systems

import os
import hashlib

# ── Helpers ──────────────────────────────────────────────────────────────────

def generate_keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    """Derive a deterministic keystream from key+nonce using SHA-256 in a simple
    counter mode. In real ciphers this is done by AES or ChaCha20 internals."""
    stream = b""
    counter = 0
    while len(stream) < length:
        block = hashlib.sha256(key + nonce + counter.to_bytes(4, "big")).digest()
        stream += block
        counter += 1
    return stream[:length]

def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte strings of equal length."""
    return bytes(x ^ y for x, y in zip(a, b))

def encrypt(plaintext: bytes, key: bytes, nonce: bytes) -> bytes:
    """Stream-cipher encryption: ciphertext = plaintext XOR keystream."""
    keystream = generate_keystream(key, nonce, len(plaintext))
    return xor_bytes(plaintext, keystream)

# decrypt is identical to encrypt for XOR stream ciphers
decrypt = encrypt

# ── Demonstration ─────────────────────────────────────────────────────────────

print("=" * 60)
print("  NONCE REUSE VULNERABILITY DEMONSTRATION")
print("=" * 60)

# The secret key — never known to the attacker
key = os.urandom(32)

# ── VULNERABLE: same nonce used for two messages ──────────────────────────────
REUSED_NONCE = b"fixed_nonce_1234"   # <-- BUG: hardcoded / reused nonce

message1 = b"TRANSFER $10000 TO ACCOUNT 99887766"
message2 = b"LAUNCH MISSILES AT DAWN COORDINATES"

ct1 = encrypt(message1, key, REUSED_NONCE)
ct2 = encrypt(message2, key, REUSED_NONCE)

print("\n[VULNERABLE] Both messages encrypted with the SAME nonce.")
print(f"  Ciphertext 1 (hex): {ct1.hex()}")
print(f"  Ciphertext 2 (hex): {ct2.hex()}")

# ── ATTACK: XOR the two ciphertexts ──────────────────────────────────────────
# ct1 XOR ct2 = (m1 XOR ks) XOR (m2 XOR ks) = m1 XOR m2  (keystream cancels!)
# If an attacker knows or guesses part of m1, they can recover m2 (and vice versa).
length = min(len(ct1), len(ct2))
xored_ciphertexts = xor_bytes(ct1[:length], ct2[:length])

# Attacker knows message1 (e.g., observed a known-plaintext or guessed the format)
recovered_m2 = xor_bytes(xored_ciphertexts, message1[:length])

print("\n[ATTACK]  Attacker XORs the two ciphertexts (key cancels out).")
print(f"  Recovered message2: {recovered_m2.decode(errors='replace')!r}")
print(f"  Actual   message2:  {message2[:length]!r}")
print(f"  Attack succeeded:   {recovered_m2 == message2[:length]}")

# ── SECURE: unique random nonce per message ───────────────────────────────────
nonce_a = os.urandom(16)   # fresh random nonce for every encryption
nonce_b = os.urandom(16)   # different nonce — keystreams are completely unrelated

ct_a = encrypt(message1, key, nonce_a
