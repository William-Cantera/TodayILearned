# TIL: Cross-Site Request Forgery (CSRF) Defenses

*Date: 2026-11-21*

## Summary / Problem Statement

CSRF attacks trick an authenticated user's browser into sending an unwanted request to a web application. Because browsers automatically attach cookies to requests, a malicious third-party site can silently perform actions on behalf of the victim — transferring funds, changing an email address, or deleting data — without the user ever knowing.

---

## Key Concepts & Technical Details

**How CSRF Works**
- The victim is logged into `bank.com` (session cookie is active).
- They visit `evil.com`, which contains a hidden `<form>` that auto-submits a POST to `bank.com/transfer`.
- The browser dutifully sends the session cookie along, and the server sees a legitimate-looking request.

**Primary Defenses**

- **Synchronizer Token Pattern (CSRF Token)**
  - Server generates a unique, unpredictable token per session (or per request).
  - Token is embedded in forms/headers and validated server-side.
  - An attacker on a different origin cannot read this token due to the Same-Origin Policy.

- **`SameSite` Cookie Attribute**
  - `SameSite=Strict` — cookie never sent on cross-site requests.
  - `SameSite=Lax` *(modern browser default)* — cookie sent on top-level navigations (GET) but blocked on cross-origin POST/fetch.
  - `SameSite=None; Secure` — required for legitimate cross-site use cases (e.g., embedded widgets).

- **Double Submit Cookie**
  - A random value is set as both a cookie and a request parameter; the server checks they match.
  - Simpler to implement in stateless APIs but weaker if subdomains are compromised.

- **Custom Request Headers**
  - APIs can require `X-Requested-With: XMLHttpRequest`; cross-origin scripts cannot set custom headers without CORS preflight approval.

---

## Practical Takeaway / Real-world Gotcha

> **`SameSite=Lax` is not a silver bullet.**

Many teams assume modern browsers handle CSRF automatically via `SameSite=Lax`. However, `Lax` still allows cookies on cross-site **GET** navigations — meaning any state-changing endpoint reachable via GET remains vulnerable. Always:

1. Ensure state-changing operations use **POST/PUT/DELETE**, never GET.
2. Pair `SameSite` cookies with **CSRF tokens** for defense-in-depth.
3. Audit third-party subdomain trust — a compromised subdomain can bypass the double-submit cookie pattern entirely.
