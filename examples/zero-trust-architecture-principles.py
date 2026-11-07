"""
Today I Learned Example: Zero Trust Architecture Principles
Date: 2026-11-06
"""

# Zero Trust Architecture Principles Demo
# "Never Trust, Always Verify" - every request must be authenticated,
# authorized, and validated regardless of network location or previous access.
#
# Core principles demonstrated:
# 1. Verify explicitly - always authenticate and authorize
# 2. Least privilege access - grant minimum required permissions
# 3. Assume breach - log everything, validate all inputs
#
# Use when: building APIs, microservices, or any system where
# internal components must not blindly trust each other.

import hashlib
import hmac
import time
import json
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ZeroTrust")

# Simulated token store: token -> {user, roles, expires_at}
# In production, use a secure token service (e.g., OAuth2/JWT with short TTLs)
TOKEN_STORE = {}
SECRET_KEY = b"super-secret-key-store-in-env-not-here"

def issue_token(user_id: str, roles: list[str], ttl_seconds: int = 30) -> str:
    """Issue a short-lived, HMAC-signed token. Short TTLs limit blast radius on compromise."""
    payload = f"{user_id}:{','.join(roles)}:{time.time()}"
    signature = hmac.new(SECRET_KEY, payload.encode(), hashlib.sha256).hexdigest()
    token = f"{payload}:{signature}"
    TOKEN_STORE[token] = {"user": user_id, "roles": roles, "expires_at": time.time() + ttl_seconds}
    logger.info(f"Token issued for user='{user_id}' roles={roles} ttl={ttl_seconds}s")
    return token

def verify_token(token: str) -> dict | None:
    """Verify token existence, signature integrity, and expiry. Never trust stale tokens."""
    entry = TOKEN_STORE.get(token)
    if not entry:
        logger.warning("Token verification failed: unknown token")
        return None
    if time.time() > entry["expires_at"]:
        del TOKEN_STORE[token]  # Purge expired tokens immediately
        logger.warning(f"Token expired for user='{entry['user']}'")
        return None
    # Re-verify HMAC signature to detect tampering
    parts = token.rsplit(":", 1)
    expected_sig = hmac.new(SECRET_KEY, parts[0].encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_sig, parts[1]):
        logger.warning("Token verification failed: signature mismatch (possible tampering)")
        return None
    return entry

def require_roles(*required_roles):
    """Decorator enforcing least-privilege: caller must hold ALL required roles.
    Principle: grant minimum permissions needed, deny by default."""
    def decorator(func):
        @wraps(func)
        def wrapper(token: str, *args, **kwargs):
            identity = verify_token(token)
            if not identity:
                raise PermissionError("Access denied: invalid or expired token")
            missing = [r for r in required_roles if r not in identity["roles"]]
            if missing:
                logger.warning(f"Authorization failed: user='{identity['user']}' missing roles={missing}")
                raise PermissionError(f"Access denied: missing roles {missing}")
            logger.info(f"Access granted: user='{identity['user']}' -> {func.__name__}()")
            return func(token, *args, **kwargs)
        return wrapper
    return decorator

def validate_input(data: dict) -> dict:
    """Always validate and sanitize inputs - assume all data is hostile (assume breach)."""
    if not isinstance(data, dict):
        raise ValueError("Input must be a dictionary")
    return {k: str(v)[:256] for k, v in data.items() if isinstance(k, str)}  # Sanitize

@require_roles("admin")
def delete_resource(token: str, resource_id: str) -> str:
    resource_id = validate_input({"id": resource_id})["id"]
    return f"Resource '{resource_id}' deleted"

@require_roles("reader")
def read_data(token: str, query: str) -> str:
    query = validate_input({"q": query})["q"]
    return f"Data for query='{query}': [record1, record2]"

# --- Demo ---
if __name__ == "__main__":
    print("\n=== Zero Trust Demo ===\n")
    admin_token = issue_token("alice", ["admin", "reader"])
    reader_token = issue_token("bob", ["reader"])

    print(read_data(admin_token, "SELECT * FROM orders"))
