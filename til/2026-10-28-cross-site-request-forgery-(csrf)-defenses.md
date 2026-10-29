# TIL: Cross-Site Request Forgery (CSRF) Defenses

*Date: 2026-10-28*

## Summary / Problem Statement

CSRF attacks trick an authenticated user's browser into making unintended requests to a web application — like transferring funds or changing an email address — without the user's knowledge. Because browsers automatically attach cookies to requests, the server can't distinguish a legitimate request from a forged one without extra defenses.

---

## Key Concepts & Technical Details

**How the Attack Works**
- Victim is logged into `bank.com` with a valid session cookie
- Attacker hosts a malicious page with a hidden form that POSTs to `bank.com/transfer`
- Victim visits the malicious page; the browser fires the request with the session cookie attached automatically

**Primary Defense: CSRF Tokens**
- Server generates a random, unpredictable token tied to the user's session
- Token is embedded in every state-changing form as a hidden field or custom request header
- Server validates the token on every `POST`, `PUT`, `PATCH`, and `DELETE` request
- Attacker cannot read or forge this token due to the **Same-Origin Policy**

**Modern Alternatives & Layered Defenses**

| Mechanism | How It Helps |
|---|---|
| `SameSite=Strict/Lax` cookie attribute | Prevents cookies from being sent on cross-site requests |
| `Origin` / `Referer` header validation | Server checks the request source matches expected origin |
| Double Submit Cookie pattern | Token is sent both as a cookie and a request parameter |
| Custom request headers (e.g., `X-Requested-With`) | Simple requests can't set custom headers cross-origin |

---

## Practical Takeaway / Real-world Gotcha

- **`SameSite=Lax` is not a silver bullet.** Top-level GET navigations still send cookies, so ensure state-changing operations never use GET.
- **Don't forget APIs.** REST APIs consumed by SPAs are still vulnerable if they rely solely on cookies — always validate the `Origin` header or use token-based auth (e.g., Bearer tokens in `Authorization` headers, which can't be set by cross-origin forms).
- **Framework defaults help, but verify.** Django, Rails, and Spring all include CSRF middleware — make sure you haven't accidentally disabled it for convenience during development and left it off in production.
