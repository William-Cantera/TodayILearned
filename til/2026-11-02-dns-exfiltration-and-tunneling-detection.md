# TIL: DNS Exfiltration and Tunneling Detection

*Date: 2026-11-02*

## Summary / Problem Statement

DNS is rarely blocked at the network perimeter, making it an attractive covert channel for attackers. DNS exfiltration encodes stolen data inside DNS query strings, while DNS tunneling establishes a full bidirectional communication channel — often used for C2 (command-and-control) or bypassing captive portals entirely.

---

## Key Concepts & Technical Details

**How it works:**
- Attackers encode payload data (files, credentials, commands) into subdomains: `aGVsbG8td29ybGQ.evil.com`
- A controlled authoritative DNS server decodes the queries and responds with encoded data in TXT, CNAME, or NULL records
- Tools like `iodine`, `dnscat2`, and `dns2tcp` automate full tunnel establishment

**Detection signals to watch for:**

- **High query volume** from a single host to a single domain — legitimate apps rarely hammer one domain
- **Abnormally long subdomain labels** — RFC 1035 allows up to 63 chars per label; base64/hex-encoded payloads often push this limit
- **High entropy subdomains** — random-looking strings score high on Shannon entropy vs. human-readable names
- **Rare or new domains** — newly registered domains with no prior resolution history are a red flag
- **Unusual record types** — frequent TXT or NULL record queries are uncommon in normal traffic
- **Low TTL values** — tunneling tools often set TTL to 0 or 1 to avoid caching and keep the channel responsive

**Useful detection queries (SIEM/log analysis):**
```
# Flag queries with subdomain length > 50 chars
# Flag domains with entropy score > 3.5 bits/char
# Alert on > 500 DNS queries/min to a single domain from one host
```

---

## Practical Takeaway / Real-world Gotcha

> Just blocking known-bad domains isn't enough — DNS tunneling thrives on *newly registered* or *algorithmically generated* domains that have no reputation yet.

Pair **entropy-based detection** with **behavioral baselines** (queries per host per domain over time). Also log DNS at the resolver level, not just the firewall — many teams miss lateral DNS traffic that never leaves the internal network. Integrate with threat intel feeds that flag domains registered within the last 30 days.
