"""
Today I Learned Example: Cryptographic Nonce Reuse Vulnerabilities
Date: 2026-11-07
"""

# Cryptographic Nonce Reuse Vulnerabilities
# This script demonstrates why reusing a nonce (number used once) in stream ciphers
# or authenticated encryption is catastrophic for security.
#
# WHEN THIS MATTERS: Any cipher operating in CTR, GCM, or similar streaming modes
# requires a unique nonce per encryption. Reusing a nonce leaks the keystream,
# allowing an attacker to recover plaintext without knowing the secret key.
#
# BEST PRACTICE: Always use a cryptographically random, never-reused nonce.

import os
import hashlib

# --- Simulated Stream Cipher (XOR with keystream derived from key+nonce) ---
# Real ciphers like AES-CTR work similarly: keystream XOR plaintext = ciphertext.

def generate_keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    """Derive a deterministic keystream from key+nonce using SHA-256 (simplified)."""
    keystream = b""
    counter = 0
    while len(keystream) < length:
        # In real CTR mode, each block uses key + nonce + incrementing counter
        block = hashlib.sha256(key + nonce + counter.to_bytes(4, "big")).digest()
        keystream += block
        counter += 1
    return keystream[:length]

def stream_encrypt(key: bytes, nonce: bytes, plaintext: bytes) -> bytes:
    """Encrypt plaintext by XORing with keystream (stream cipher simulation)."""
    ks = generate_keystream(key, nonce, len(plaintext))
    return bytes(p ^ k for p, k in zip(plaintext, ks))

# XOR decryption is identical to encryption in a stream cipher
stream_decrypt = stream_encrypt

# --- THE VULNERABILITY: Nonce Reuse ---
# If the same (key, nonce) pair encrypts two messages:
#   C1 = P1 XOR KS
#   C2 = P2 XOR KS
# Then: C1 XOR C2 = P1 XOR P2  (keystream cancels out!)
# An attacker who knows or guesses part of P1 can recover P2, and vice versa.

def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte strings together (up to the length of the shorter one)."""
    return bytes(x ^ y for x, y in zip(a, b))

# --- Setup: Secret key (never shared) ---
SECRET_KEY = os.urandom(32)  # 256-bit key, kept secret

# --- VULNERABLE SCENARIO: Nonce reused for two different messages ---
REUSED_NONCE = b"fixed_nonce_001"  # BAD: hardcoded/reused nonce

message1 = b"Transfer $1000 to Alice account"
message2 = b"Transfer $9000 to Eve's account!"

cipher1 = stream_encrypt(SECRET_KEY, REUSED_NONCE, message1)
cipher2 = stream_encrypt(SECRET_KEY, REUSED_NONCE, message2)

print("=== NONCE REUSE ATTACK DEMONSTRATION ===\n")
print(f"Ciphertext 1 (hex): {cipher1.hex()}")
print(f"Ciphertext 2 (hex): {cipher2.hex()}\n")

# --- ATTACKER'S PERSPECTIVE ---
# Attacker intercepts both ciphertexts and XORs them together
xored_ciphertexts = xor_bytes(cipher1, cipher2)
print(f"C1 XOR C2 (hex):    {xored_ciphertexts.hex()}")
print("(This equals P1 XOR P2 — keystream is completely eliminated!)\n")

# If attacker knows/guesses message1 (e.g., a known plaintext attack),
# they can recover message2 entirely without the key!
recovered_message2 = xor_bytes(xored_ciphertexts, message1)
print(f"Known plaintext (P1):      {message1.decode()}")
print(f"Recovered P2 (no key!):    {recovered_message2.decode()}")
print(f"Attack succeeded: {recovered_message2 == message2}\n")

# --- SECURE SCENARIO: Fresh random nonce for every encryption ---
print("=== SECURE USAGE: UNIQUE NONCE PER MESSAGE ===\n")

nonce_a = os.urandom(16)  # GOOD: cryptographically random nonce
nonce_b = os.urandom(16)  # GOOD: different nonce for each message

secure_cipher1 = stream_encrypt(SECRET_KEY, nonce_a, message1)
secure_cipher2 = stream_encrypt(SECRET_KEY, nonce_b, message2)

# XOR
