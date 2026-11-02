"""
Today I Learned Example: Reverse Proxy Header Hardening (X-Forwarded-For)
Date: 2026-11-01
"""

# Reverse Proxy Header Hardening (X-Forwarded-For)
#
# WHAT THIS PATTERN DOES:
# When your app sits behind a reverse proxy (Nginx, AWS ALB, Cloudflare, etc.),
# the real client IP is passed via the X-Forwarded-For (XFF) header.
# Format: "client, proxy1, proxy2" (leftmost = original client)
#
# WHY IT MATTERS:
# Attackers can SPOOF X-Forwarded-For by sending their own header value.
# If your app naively trusts XFF, an attacker can fake their IP to bypass
# rate limiting, geo-restrictions, or audit logging.
#
# THE SAFE APPROACH:
# Only trust N rightmost IPs added by YOUR known/trusted proxies.
# The rightmost IP is always added by the last proxy your server talked to
# directly — that one cannot be spoofed by the client.
#
# BEST PRACTICES:
# 1. Configure exactly how many trusted proxies sit in front of your app.
# 2. Strip/ignore client-supplied XFF entries beyond that count.
# 3. Validate extracted IPs are well-formed.
# 4. Never trust XFF at all if you have no proxies.

import ipaddress
from http.server import BaseHTTPRequestHandler, HTTPServer


# Number of trusted reverse proxies in front of this application.
# Example: 1 if you have one Nginx instance, 2 if Nginx + a load balancer.
TRUSTED_PROXY_COUNT = 1


def extract_real_client_ip(xff_header: str, remote_addr: str, trusted_proxies: int) -> str:
    """
    Safely extract the real client IP from X-Forwarded-For.

    Args:
        xff_header:      Raw value of the X-Forwarded-For header (may be empty).
        remote_addr:     The TCP-level peer address (always trustworthy — OS-provided).
        trusted_proxies: How many proxies you control and trust.

    Returns:
        A validated IP string representing the real client.
    """
    if trusted_proxies == 0 or not xff_header:
        # No proxies configured, or no header present — use the direct TCP peer.
        return remote_addr

    # Split the XFF chain and strip whitespace from each entry.
    # Example: "1.2.3.4, 10.0.0.1, 10.0.0.2" → ["1.2.3.4", "10.0.0.1", "10.0.0.2"]
    ip_chain = [ip.strip() for ip in xff_header.split(",")]

    # The rightmost `trusted_proxies` entries were added by our own infrastructure.
    # Everything to the LEFT of those is either the real client or attacker-controlled.
    # We want the entry just to the left of our trusted proxy additions.
    #
    # Safe index: len(chain) - trusted_proxies - 1
    # If the chain is too short (attacker didn't send enough hops), fall back to remote_addr.
    safe_index = len(ip_chain) - trusted_proxies - 1

    if safe_index < 0:
        # Chain is shorter than expected — the header may be missing entries.
        # Fall back to the direct peer address to avoid trusting spoofed data.
        return remote_addr

    candidate_ip = ip_chain[safe_index]

    # Validate the extracted value is actually a valid IP address.
    try:
        ipaddress.ip_address(candidate_ip)
        return candidate_ip
    except ValueError:
        # Malformed IP in the header — fall back to safe peer address.
        return remote_addr


class HardenedHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler demonstrating hardened XFF extraction."""

    def do_GET(self):
        xff = self.headers.get("X-Forwarded-For", "")
        # self.client_address[0] is the OS-level TCP peer (e.g., your Nginx IP).
        remote_addr = self.client_address[0]

        real_ip = extract_real_client_ip(xff, remote_addr, TRUSTED_PROXY_COUNT)

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        response = (
            f"TCP peer (remote_addr): {remote_addr}\n"
            f"X-Forwarded-For header: {xff or '(none)'}\n"
            f"Resolved real client IP: {real_ip}\n"
            f"Trusted proxy count:     {TRUSTED_PROXY_COUNT}\n"
        )
        self.wfile.write(response.encode())

    def log_message(self, fmt, *args):
        # Suppress default server log noise for cleaner demo output
