# TIL: JWT Header Injection and Validation Flaws

*Date: 2026-10-21*

## Summary / Problem Statement

JSON Web Tokens (JWTs) are widely used for authentication, but their flexibility in the header section introduces critical validation vulnerabilities. Attackers can manipulate JWT headers to bypass signature verification entirely — a subtle flaw that has burned real production systems.

---

## Key Concepts & Technical Details

A JWT consists of three Base64URL-encoded parts: **header**, **payload**, and **signature**. The header declares the algorithm used to sign the token.

**Common attack vectors:**

- **`alg: none` attack**
  - An attacker changes the `alg` field to `"none"`, strips the signature, and submits the token
  - Vulnerable libraries that blindly trust the header will skip verification and accept the token as valid

- **Algorithm confusion (RS256 → HS256)**
  - If a server uses RS256 (asymmetric), its *public key* is often discoverable
  - An attacker switches `alg` to `HS256` (symmetric) and re-signs the token using the **public key as the HMAC secret**
  - A naive verifier using the public key with HS256 will validate it successfully

- **`jwk` / `jku` header injection**
  - The `jwk` header embeds a JSON Web Key directly; `jku` points to a URL hosting a key set
  - If the server fetches and trusts an attacker-controlled `jku` URL, the attacker supplies their own public key and signs a forged token that passes verification

**Why it happens:**
- Libraries that derive the verification algorithm *from the token itself* rather than enforcing it server-side
- Missing allowlists for trusted `jku` URLs
- Overly permissive JWT parsing defaults

---

## Practical Takeaway / Real-world Gotcha

> **Never let the token dictate how it should be verified.**

- ✅ **Hardcode the expected algorithm** on the server — never read `alg` from the incoming token header
- ✅ **Maintain an explicit allowlist** of trusted `jku` URLs; reject anything else
- ✅ Disable `alg: none` support at the library configuration level (many libraries require an explicit opt-out)
- ✅ Prefer well-audited libraries (`python-jose`, `jsonwebtoken` with strict options) and review their default behaviors on each upgrade
- ✅ Treat JWTs as **untrusted input** until the signature is verified against a server-controlled key and algorithm
