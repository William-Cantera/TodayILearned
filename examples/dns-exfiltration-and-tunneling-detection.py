"""
Today I Learned Example: DNS Exfiltration and Tunneling Detection
Date: 2026-11-22
"""

# DNS Exfiltration and Tunneling Detection
# This script demonstrates how to detect potential DNS-based data exfiltration
# and tunneling attacks by analyzing DNS query patterns and characteristics.
#
# DNS tunneling works by encoding data into DNS queries/responses, allowing
# attackers to bypass firewalls and exfiltrate data covertly.
#
# When to use: Network security monitoring, SOC analysis, IDS/IPS rule development
# Best practices: Combine multiple detection signals, maintain baseline thresholds,
#                 correlate with other network telemetry for fewer false positives

import re
import math
import collections
from datetime import datetime, timedelta
import random
import string

# --- Entropy Calculation ---
# High entropy in subdomains indicates encoded/encrypted data (base64, hex, etc.)
# Legitimate domains like "www.google.com" have low entropy; tunneled data is random-looking

def calculate_entropy(text):
    """Shannon entropy measures randomness. Values > 3.5 suggest encoded payloads."""
    if not text:
        return 0.0
    freq = collections.Counter(text.lower())
    length = len(text)
    return -sum((count / length) * math.log2(count / length) for count in freq.values())

# --- Subdomain Length Check ---
# Legitimate subdomains are typically short (www, mail, api).
# DNS tunneling tools encode chunks of data, producing unusually long subdomains.

def check_subdomain_length(domain, threshold=40):
    """Flag subdomains exceeding typical length. Tunneling tools often use 50-63 char subdomains."""
    parts = domain.split('.')
    subdomain = '.'.join(parts[:-2]) if len(parts) > 2 else ''
    return len(subdomain) > threshold, len(subdomain), subdomain

# --- Query Frequency Analysis ---
# Tunneling generates high-frequency queries to the same domain (acting as a channel).
# Normal users rarely query the same TLD hundreds of times per minute.

def analyze_query_frequency(query_log, time_window_seconds=60, threshold=50):
    """Detect domains queried suspiciously often within a time window."""
    domain_counts = collections.Counter()
    cutoff = datetime.now() - timedelta(seconds=time_window_seconds)
    for timestamp, domain in query_log:
        if timestamp >= cutoff:
            # Extract base domain (last two parts) to group subdomains together
            parts = domain.split('.')
            base = '.'.join(parts[-2:]) if len(parts) >= 2 else domain
            domain_counts[base] += 1
    return {d: c for d, c in domain_counts.items() if c >= threshold}

# --- Unique Subdomain Detection ---
# Tunneling generates many unique subdomains per base domain (each query = new data chunk).
# Legitimate services reuse a small set of subdomains consistently.

def detect_unique_subdomains(query_log, threshold=20):
    """Flag base domains with too many unique subdomains — classic tunneling indicator."""
    subdomain_map = collections.defaultdict(set)
    for _, domain in query_log:
        parts = domain.split('.')
        if len(parts) > 2:
            base = '.'.join(parts[-2:])
            subdomain_map[base].add('.'.join(parts[:-2]))
    return {d: len(subs) for d, subs in subdomain_map.items() if len(subs) >= threshold}

# --- Simulate DNS Query Log ---
# Generates realistic benign traffic mixed with simulated tunneling activity

def generate_simulated_log():
    now = datetime.now()
    log = []
    # Benign traffic: normal browsing patterns
    benign = ['www.google.com', 'mail.yahoo.com', 'api.github.com', 'cdn.cloudflare.com']
    for domain in benign:
        for _ in range(random.randint(3, 8)):
            log.append((now - timedelta(seconds=random.randint(0, 59)), domain))
    # Malicious traffic: simulate iodine/dnscat-style tunneling to evil.com
    for _ in range(60):
        # Random high-entropy subdomain simulating base32-encoded payload chunks
        chunk = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(45, 60)))
        log.append((now - timedelta(seconds=random.randint(0, 59)), f"{chunk}.evil.com"))
    return log

# --- Main Detection Engine ---
if __name__ == '__main__':
    print("=== DNS Exfiltration & Tunneling Detector ===\n")
    log = generate_simulated_log()

    # Check 1: Entropy and length analysis per query
    print("[*] Analyzing individual queries for high-entropy
