# TIL: Reverse Proxy Header Hardening (X-Forwarded-For)

*Date: 2026-11-08*

## Summary / Problem Statement

When running applications behind a reverse proxy (Nginx, Cloudflare, AWS ALB, etc.), you often rely on the `X-Forwarded-For` (XFF) header to identify the real client IP. The problem: **this header is trivially spoofable by clients**, and blindly trusting it can lead to broken rate limiting, incorrect audit logs, or bypassed IP allowlists.

---

## Key Concepts & Technical Details

**How `X-Forwarded-For` works:**
- Each proxy in the chain *appends* the IP it received the request from
- Format: `X-Forwarded-For: client, proxy1, proxy2`
- The **leftmost** IP is claimed by the original client — and is fully attacker-controlled

**The trust chain problem:**
- If your app reads `req.headers['x-forwarded-for'].split(',')[0]`, an attacker can send `X-Forwarded-For: 127.0.0.1` and appear to be localhost
- This can bypass IP-based restrictions entirely

**Correct hardening approach:**

- **Know your proxy depth.** If you have exactly one trusted proxy, the real client IP is the *second-to-last* entry (or the value of `X-Real-IP` set by Nginx)
- **Strip untrusted XFF headers at the edge.** Configure your reverse proxy to *overwrite*, not append, the header before it reaches your app:
  ```nginx
  proxy_set_header X-Forwarded-For $remote_addr;
  ```
- **Use `REMOTE_ADDR` inside your trusted network.** Only the socket-level IP (set by the OS) is unforgeable
- **Framework-level settings matter.** Express.js has `app.set('trust proxy', 1)` — setting it to `true` trusts *all* proxies, which is dangerous in public deployments

---

## Practical Takeaway / Real-world Gotcha

> **The rightmost IP you *know* came from a trusted proxy is the safe one to use.**

A common production incident pattern: a security team adds IP allowlisting to an admin endpoint, tests it successfully, then discovers an attacker bypassed it by spoofing the XFF header — because the app was configured to trust the leftmost value.

- Always document how many proxy hops exist in your infrastructure
- Audit framework proxy-trust settings during security reviews
- Prefer `X-Real-IP` (set explicitly by Nginx) over raw XFF parsing when possible
