# TIL: OWASP Top 10 API Security Risks

*Date: 2026-11-24*

## Summary / Problem Statement

APIs are the backbone of modern applications, but they introduce unique attack surfaces that traditional web security checklists often miss. The OWASP API Security Top 10 specifically targets vulnerabilities common in REST, GraphQL, and other API architectures — many of which have led to high-profile data breaches.

---

## Key Concepts & Technical Details

The OWASP API Security Top 10 (2023 edition) highlights these critical risk categories:

- **API1 – Broken Object Level Authorization (BOLA):** Attackers manipulate object IDs in requests to access other users' data. The most prevalent API flaw.
- **API2 – Broken Authentication:** Weak token handling, missing expiry, or flawed credential flows allow account takeovers.
- **API3 – Broken Object Property Level Authorization:** Exposing or allowing modification of sensitive object properties users shouldn't access (replaces Mass Assignment + Excessive Data Exposure).
- **API4 – Unrestricted Resource Consumption:** No rate limiting on expensive operations leads to DoS or runaway cloud costs.
- **API5 – Broken Function Level Authorization:** Admin-only endpoints accessible to regular users due to missing role checks.
- **API6 – Unrestricted Access to Sensitive Business Flows:** Bots abuse legitimate flows (e.g., bulk ticket purchasing, credential stuffing) without triggering alerts.
- **API7 – Server-Side Request Forgery (SSRF):** User-supplied URLs cause the server to make internal requests, leaking cloud metadata or internal services.
- **API8 – Security Misconfiguration:** Default credentials, verbose error messages, unnecessary HTTP methods, or missing CORS policies.
- **API9 – Improper Inventory Management:** Shadow APIs or deprecated versions left running without security controls.
- **API10 – Unsafe Consumption of APIs:** Trusting third-party API responses without validation, enabling injection or data integrity attacks.

---

## Practical Takeaway / Real-world Gotcha

> **BOLA is deceptively simple and brutally effective.**

A common gotcha: developers secure the *user list* endpoint but forget that `GET /api/orders/{id}` has no ownership check. Any authenticated user can enumerate order IDs and read others' data.

**Quick wins:**
- Always validate *who owns* the requested resource, not just *whether the user is authenticated*
- Run `OWASP ZAP` or `42Crunch` scans against your API schema before shipping
- Treat your API changelog as a security artifact — deprecated endpoints are forgotten attack surfaces
