"""
Today I Learned Example: JWT Header Injection and Validation Flaws
Date: 2026-10-22
"""

# JWT Header Injection and Validation Flaws - Educational Demonstration
# This script shows common JWT vulnerabilities and how to defend against them.
# JWTs (JSON Web Tokens) are widely used for authentication/authorization.
# Flaws in validation logic can allow attackers to forge tokens.

import json
import base64
import hmac
import hashlib

# --- Utility Functions ---

def b64url_encode(data: bytes) -> str:
    """Base64url encode without padding (standard JWT encoding)."""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def b64url_decode(s: str) -> bytes:
    """Base64url decode, adding padding as needed."""
    padding = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + '=' * (padding % 4))

def create_jwt(payload: dict, secret: str, algorithm: str = "HS256") -> str:
    """Create a signed JWT token using HMAC-SHA256."""
    header = {"alg": algorithm, "typ": "JWT"}
    header_enc = b64url_encode(json.dumps(header, separators=(',', ':')).encode())
    payload_enc = b64url_encode(json.dumps(payload, separators=(',', ':')).encode())
    signing_input = f"{header_enc}.{payload_enc}"
    signature = hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{b64url_encode(signature)}"

# --- FLAW 1: Algorithm Confusion / "alg: none" Attack ---
# An attacker removes the signature and sets alg to "none".
# A VULNERABLE validator that trusts the header's alg field will accept it.

def vulnerable_validate_jwt(token: str, secret: str) -> dict:
    """
    VULNERABLE: Reads the algorithm from the token's own header.
    An attacker can set alg='none' and strip the signature entirely.
    NEVER trust the algorithm declared inside the token.
    """
    parts = token.split('.')
    header = json.loads(b64url_decode(parts[0]))
    payload = json.loads(b64url_decode(parts[1]))
    alg = header.get("alg", "").lower()

    if alg == "none":
        # BUG: Accepts unsigned tokens with no verification!
        print("  [VULNERABLE] Accepted 'none' algorithm — no signature checked!")
        return payload

    provided_sig = b64url_decode(parts[2])
    expected_sig = hmac.new(secret.encode(), f"{parts[0]}.{parts[1]}".encode(), hashlib.sha256).digest()
    if hmac.compare_digest(provided_sig, expected_sig):
        return payload
    raise ValueError("Invalid signature")

def secure_validate_jwt(token: str, secret: str, expected_alg: str = "HS256") -> dict:
    """
    SECURE: Algorithm is enforced by the SERVER, not read from the token header.
    This prevents algorithm confusion and 'alg: none' attacks.
    Best practice: always pin the expected algorithm on the server side.
    """
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError("Malformed token: expected 3 parts")

    header = json.loads(b64url_decode(parts[0]))
    alg_in_token = header.get("alg", "")

    # SECURE: Reject if the header claims a different algorithm
    if alg_in_token != expected_alg:
        raise ValueError(f"Algorithm mismatch: got '{alg_in_token}', expected '{expected_alg}'")

    payload = json.loads(b64url_decode(parts[1]))
    provided_sig = b64url_decode(parts[2])
    expected_sig = hmac.new(secret.encode(), f"{parts[0]}.{parts[1]}".encode(), hashlib.sha256).digest()

    # SECURE: Use constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(provided_sig, expected_sig):
        raise ValueError("Signature verification failed")

    return payload

# --- FLAW 2: Forging a token with "alg: none" ---
def forge_none_alg_token(payload: dict) -> str:
    """Attacker forges a token with alg='none' and no signature."""
    header = {"alg": "none", "typ": "JWT"}
    header_enc = b64url_encode(json.dumps(header, separators=(',', ':')).encode())
    payload_enc = b64url_encode(json.dumps(payload, separators=(',', ':')).encode())
    return f"{header_enc}.{payload_enc}."  # Empty
