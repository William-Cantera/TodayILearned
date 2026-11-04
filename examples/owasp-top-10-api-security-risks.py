"""
Today I Learned Example: OWASP Top 10 API Security Risks
Date: 2026-11-03
"""

# OWASP Top 10 API Security Risks - Educational Demonstration
# This script illustrates common API security vulnerabilities and their mitigations
# using only Python standard library modules.

import json
import hashlib
import hmac
import secrets
import re
from urllib.parse import urlparse

# ─────────────────────────────────────────────────────────────────────────────
# RISK 1: Broken Object Level Authorization (BOLA)
# Attackers substitute another user's ID to access their data.
# Mitigation: Always verify the requesting user owns the resource.
# ─────────────────────────────────────────────────────────────────────────────
def get_order(requesting_user_id: str, order_id: str, orders_db: dict) -> dict:
    order = orders_db.get(order_id)
    if not order:
        return {"error": "Order not found"}
    # SECURE: check ownership before returning data
    if order["owner"] != requesting_user_id:
        return {"error": "403 Forbidden – you do not own this resource"}
    return order

# ─────────────────────────────────────────────────────────────────────────────
# RISK 2: Broken Authentication
# Weak tokens or no expiry allow session hijacking.
# Mitigation: Use cryptographically secure tokens with HMAC signing.
# ─────────────────────────────────────────────────────────────────────────────
SECRET_KEY = secrets.token_bytes(32)   # generated once at startup; store securely

def generate_token(user_id: str) -> str:
    """Create a signed token: payload.signature"""
    payload = user_id.encode()
    sig = hmac.new(SECRET_KEY, payload, hashlib.sha256).hexdigest()
    return f"{user_id}.{sig}"

def verify_token(token: str) -> str | None:
    """Return user_id if valid, None otherwise."""
    try:
        user_id, sig = token.rsplit(".", 1)
        expected = hmac.new(SECRET_KEY, user_id.encode(), hashlib.sha256).hexdigest()
        # SECURE: constant-time comparison prevents timing attacks
        if hmac.compare_digest(expected, sig):
            return user_id
    except ValueError:
        pass
    return None

# ─────────────────────────────────────────────────────────────────────────────
# RISK 3: Excessive Data Exposure
# APIs returning full DB objects expose sensitive fields.
# Mitigation: Whitelist only the fields clients actually need.
# ─────────────────────────────────────────────────────────────────────────────
def serialize_user(user: dict) -> dict:
    ALLOWED_FIELDS = {"id", "username", "email"}   # never expose password_hash, ssn, etc.
    return {k: v for k, v in user.items() if k in ALLOWED_FIELDS}

# ─────────────────────────────────────────────────────────────────────────────
# RISK 4: Lack of Resource & Rate Limiting
# Unbounded requests enable DoS and brute-force attacks.
# Mitigation: Track request counts per client; reject when threshold exceeded.
# ─────────────────────────────────────────────────────────────────────────────
request_counts: dict[str, int] = {}
RATE_LIMIT = 5

def check_rate_limit(client_ip: str) -> bool:
    """Returns True if request is allowed, False if rate-limited."""
    count = request_counts.get(client_ip, 0) + 1
    request_counts[client_ip] = count
    return count <= RATE_LIMIT   # production: use sliding window + TTL store

# ─────────────────────────────────────────────────────────────────────────────
# RISK 5: Injection (SQL / Command)
# Unsanitised input passed to interpreters executes attacker commands.
# Mitigation: Validate & whitelist input; never concatenate into queries.
# ─────────────────────────────────────────────────────────────────────────────
def safe_username_check(username: str) -> bool:
    """Allow only alphanumeric + underscore; block injection payloads."""
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,30}", username))

# ─────────────────────────────────────────────────────────────────────────────
# RISK 6: Security Misconfiguration – verbose error messages leak internals.
# Mitigation: Return generic errors to clients; log details server-side only.
# ─────────────────────────────────────────────────────────────────────────────
def safe_error_response(exception: Exception) -> dict:
    import logging
    logging.
