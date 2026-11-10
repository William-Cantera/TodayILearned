"""
Today I Learned Example: DNS Exfiltration and Tunneling Detection
Date: 2026-11-09
"""

# DNS Exfiltration and Tunneling Detection
# This script demonstrates how to detect DNS-based data exfiltration and tunneling
# by analyzing DNS query patterns. Attackers often encode stolen data in DNS queries
# (subdomains) or use DNS as a covert communication channel to bypass firewalls.
#
# When to use: Network security monitoring, incident response, SOC analysis
# Best practices: Combine with threat intel feeds, baseline normal DNS traffic first,
# tune thresholds per environment, alert on anomalies rather than block blindly

import re
import math
import hashlib
from collections import defaultdict, Counter
from datetime import datetime

# --- Simulated DNS query log (in production, parse real DNS logs or pcap data) ---
# Format: (timestamp, source_ip, queried_domain)
DNS_QUERIES = [
    ("2024-01-15 10:00:01", "192.168.1.10", "google.com"),
    ("2024-01-15 10:00:02", "192.168.1.10", "github.com"),
    ("2024-01-15 10:00:03", "192.168.1.55", "aGVsbG8td29ybGQ.evil.com"),       # base64-like
    ("2024-01-15 10:00:04", "192.168.1.55", "dGhpcyBpcyBzZWNyZXQ.evil.com"),   # base64-like
    ("2024-01-15 10:00:05", "192.168.1.55", "c2Vuc2l0aXZlZGF0YQ.evil.com"),    # base64-like
    ("2024-01-15 10:00:06", "192.168.1.20", "normal-site.org"),
    ("2024-01-15 10:00:07", "192.168.1.33", "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4.tunnel.net"),  # hex-like
    ("2024-01-15 10:00:08", "192.168.1.33", "deadbeefcafebabe0123456789abcdef.tunnel.net"),  # hex-like
    ("2024-01-15 10:00:09", "192.168.1.33", "0011223344556677889900aabbccddee.tunnel.net"),  # hex-like
    ("2024-01-15 10:00:10", "192.168.1.10", "stackoverflow.com"),
    ("2024-01-15 10:00:11", "192.168.1.77", "xn--nxasmq6b.xn--nxasmq6b.xn--nxasmq6b.weird.io"),  # punycode abuse
    ("2024-01-15 10:00:12", "192.168.1.55", "ZmluYWxjaHVuaw.evil.com"),         # base64-like
    ("2024-01-15 10:00:13", "192.168.1.33", "ffee1122334455667788990011223344.tunnel.net"),
]

def calculate_entropy(data: str) -> float:
    """
    Shannon entropy measures randomness in a string.
    High entropy (>3.5) in subdomains suggests encoded/encrypted data.
    Legitimate domains have low entropy; tunneled data has high entropy.
    """
    if not data:
        return 0.0
    freq = Counter(data)
    length = len(data)
    return -sum((count / length) * math.log2(count / length) for count in freq.values())

def extract_subdomain(domain: str) -> str:
    """Extract the leftmost subdomain label for analysis."""
    parts = domain.split(".")
    return parts[0] if len(parts) > 2 else ""

def detect_encoding(subdomain: str) -> list:
    """
    Detect common encoding schemes used in DNS exfiltration:
    - Base64: alphanumeric + /+=, length multiple of 4
    - Hex: only 0-9a-f characters, even length
    """
    indicators = []
    if re.match(r'^[A-Za-z0-9+/=\-_]+$', subdomain) and len(subdomain) > 20:
        # Base64url is common in DNS tunneling (replaces + with - and / with _)
        indicators.append("possible_base64_encoding")
    if re.match(r'^[0-9a-fA-F]+$', subdomain) and len(subdomain) >= 16:
        indicators.append("possible_hex_encoding")
    return indicators

def analyze_dns_logs(queries: list) -> dict:
