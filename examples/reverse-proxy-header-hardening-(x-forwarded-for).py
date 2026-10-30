"""
Today I Learned Example: Reverse Proxy Header Hardening (X-Forwarded-For)
Date: 2026-10-29
"""

# Reverse Proxy Header Hardening (X-Forwarded-For)
#
# WHAT THIS PATTERN DOES:
# When your application sits behind a reverse proxy (nginx, AWS ALB, Cloudflare, etc.),
# the client's real IP address is passed via the X-Forwarded-For (XFF) header.
# Format: X-Forwarded-For: client, proxy1, proxy2
#
# WHY IT MATTERS:
# If you blindly trust X-Forwarded-For, attackers can spoof their IP address by
# sending: X-Forwarded-For: 127.0.0.1, attacker_controlled_value
# This breaks IP-based rate limiting, geo-blocking, and audit logging.
#
# THE FIX:
# Only trust a known number of proxy hops from the RIGHT side of the header.
# Your infrastructure controls the rightmost entries; clients control the leftmost.
#
# BEST PRACTICES:
# 1. Set TRUSTED_PROXY_COUNT to exactly how many proxies sit in front of your app.
# 2. Never trust the full header chain blindly.
# 3. Validate extracted IPs — reject malformed values.
# 4. If no proxy sits in front, use REMOTE_ADDR directly and ignore XFF entirely.

import ipaddress
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

# How many reverse proxies sit in front of this application.
# Set this to match your actual infrastructure (e.g., 1 for a single nginx).
TRUSTED_PROXY_COUNT = 1

# Simple regex for basic IP format sanity check before full parsing
_IP_RE = re.compile(r'^[\d\.a-fA-F:]+$')


def get_real_client_ip(xff_header: str | None, remote_addr: str) -> str:
    """
    Extract the real client IP from X-Forwarded-For using a fixed proxy count.

    Args:
        xff_header:  Value of the X-Forwarded-For header (may be None or spoofed).
        remote_addr: The direct TCP connection IP (REMOTE_ADDR) — always trustworthy.

    Returns:
        A validated IP string, or remote_addr as a safe fallback.
    """
    # If no proxies are configured, ignore XFF entirely — use the direct connection IP.
    if TRUSTED_PROXY_COUNT == 0 or not xff_header:
        return remote_addr

    # Split the header into individual hops and strip whitespace.
    # Example: "1.2.3.4, 10.0.0.1, 172.16.0.1"  →  ["1.2.3.4", "10.0.0.1", "172.16.0.1"]
    hops = [h.strip() for h in xff_header.split(',')]

    # The rightmost N entries were added by our trusted proxies.
    # The entry just to the LEFT of those is the real client IP.
    # Index calculation: -(TRUSTED_PROXY_COUNT + 1) from the right.
    target_index = -(TRUSTED_PROXY_COUNT + 1)

    if len(hops) < TRUSTED_PROXY_COUNT + 1:
        # Not enough hops — header may be missing entries; fall back to REMOTE_ADDR.
        return remote_addr

    candidate = hops[target_index]

    # Validate the candidate looks like an IP address before using it.
    if not _IP_RE.match(candidate):
        return remote_addr  # Reject garbage values

    try:
        # ipaddress.ip_address() strictly validates IPv4 and IPv6 format.
        validated = str(ipaddress.ip_address(candidate))
        return validated
    except ValueError:
        # Malformed value — fall back to the safe direct-connection IP.
        return remote_addr


class HardenedHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler that demonstrates hardened IP extraction."""

    def do_GET(self):
        xff = self.headers.get('X-Forwarded-For')
        remote_addr = self.client_address[0]

        real_ip = get_real_client_ip(xff, remote_addr)

        response = (
            f"REMOTE_ADDR      : {remote_addr}\n"
            f"X-Forwarded-For  : {xff or '(not set)'}\n"
            f"Resolved Real IP : {real_ip}\n"
            f"Trusted Proxies  : {TRUSTED_PROXY_COUNT}\n"
        )
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(response.encode())

    def log_message(self, fmt, *args):  # Suppress default access log noise
        pass


if __name
