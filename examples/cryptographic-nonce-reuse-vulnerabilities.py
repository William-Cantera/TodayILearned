"""
Today I Learned Example: Cryptographic Nonce Reuse Vulnerabilities
Date: 2026-11-10
"""

# Cryptographic Nonce Reuse Vulnerabilities
# This script demonstrates why reusing a nonce (number used once) in stream ciphers
# is catastrophically dangerous. We simulate a simplified XOR stream cipher to show
# how an attacker can recover plaintexts when the same keystream is used twice.
#
# WHEN THIS MATTERS: Any stream cipher (RC4, CTR mode AES, ChaCha20, OTP) becomes
# completely broken when the same key+nonce combination encrypts two messages.
#
# BEST PRACTICE: Always use a fresh, random nonce for each encryption operation.

import os
import secrets

# ── Helpers ──────────────────────────────────────────────────────────────────

def generate_keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    """
    Simulate a stream cipher keystream using a simple PRNG seeded by key+nonce.
    In real life this would be ChaCha20 or AES-CTR; the vulnerability is the same.
    WARNING: This PRNG is NOT cryptographically secure – for demo purposes only.
    """
    import hashlib
    seed = key + nonce
    stream = b""
    counter = 0
    while len(stream) < length:
        # Derive pseudo-random bytes by hashing seed + counter block
        block = hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
        stream += block
        counter += 1
    return stream[:length]

def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte strings of equal length."""
    return bytes(x ^ y for x, y in zip(a, b))

def encrypt(plaintext: bytes, key: bytes, nonce: bytes) -> bytes:
    """Encrypt plaintext using the simulated stream cipher."""
    keystream = generate_keystream(key, nonce, len(plaintext))
    return xor_bytes(plaintext, keystream)

# ── Vulnerability Demo ────────────────────────────────────────────────────────

print("=" * 60)
print("DEMO 1: Nonce REUSE – catastrophic key-stream exposure")
print("=" * 60)

# Alice and Bob share a secret key
SECRET_KEY = secrets.token_bytes(32)

# !! BUG: The same nonce is reused for two different messages !!
REUSED_NONCE = b"\x00" * 12   # A common mistake: hardcoded or zeroed nonce

message_A = b"Attack at dawn!!"
message_B = b"Retreat to base!"

cipher_A = encrypt(message_A, SECRET_KEY, REUSED_NONCE)
cipher_B = encrypt(message_B, SECRET_KEY, REUSED_NONCE)

print(f"Ciphertext A : {cipher_A.hex()}")
print(f"Ciphertext B : {cipher_B.hex()}")

# ── Attack: XOR the two ciphertexts ──────────────────────────────────────────
# Because: C_A = P_A XOR K  and  C_B = P_B XOR K
# Therefore: C_A XOR C_B = P_A XOR P_B  (keystream cancels out!)
xor_of_ciphers = xor_bytes(cipher_A, cipher_B)
xor_of_plains  = xor_bytes(message_A, message_B)

print(f"\nC_A XOR C_B  : {xor_of_ciphers.hex()}")
print(f"P_A XOR P_B  : {xor_of_plains.hex()}")
print(f"They match   : {xor_of_ciphers == xor_of_plains}")

# If attacker knows (or guesses) message_A, they recover message_B instantly:
recovered_B = xor_bytes(xor_of_ciphers, message_A)
print(f"\nAttacker recovers message B: {recovered_B}")

# ── Safe Demo ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("DEMO 2: Unique nonces – secure usage")
print("=" * 60)

# BEST PRACTICE: generate a fresh random nonce per message
nonce_1 = os.urandom(12)   # 96-bit nonce, cryptographically random
nonce_2 = os.urandom(12)   # Different nonce for every message

safe_cipher_A = encrypt(message_A, SECRET_KEY, nonce_1)
safe_cipher_B = encrypt(message_B, SECRET_KEY, nonce_2)

xor_safe = xor_bytes(safe_cipher_A, safe_cipher_B)
print(f"Safe C_A XOR C_
