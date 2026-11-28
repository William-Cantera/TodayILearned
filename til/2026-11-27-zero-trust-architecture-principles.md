# TIL: Zero Trust Architecture Principles

*Date: 2026-11-27*

## Summary / Problem Statement

Traditional network security assumed that everything inside the corporate perimeter could be trusted. Once an attacker breached the firewall, they could move laterally almost unchecked. Zero Trust Architecture (ZTA) was designed to eliminate this implicit trust — **never trust, always verify**.

---

## Key Concepts & Technical Details

Zero Trust is a security model, not a single product. It rests on a few foundational principles:

- **Verify Explicitly**
  Every access request is authenticated and authorized based on *all available signals* — identity, device health, location, and behavior — regardless of where the request originates.

- **Use Least Privilege Access**
  Users and services receive only the minimum permissions needed for their task. This limits the blast radius of a compromised account.

- **Assume Breach**
  Design systems as if an attacker is already inside. This drives micro-segmentation, end-to-end encryption, and robust logging.

**Core components typically involved:**

- **Identity Provider (IdP):** Centralized authentication (e.g., Azure AD, Okta) with MFA enforced.
- **Policy Engine / Policy Enforcement Point (PEP):** Evaluates contextual signals and grants or denies access dynamically.
- **Device Trust:** Endpoints must meet a health baseline (patched OS, MDM enrolled) before access is granted.
- **Micro-segmentation:** Network is divided into small zones; east-west traffic between services is also authenticated and authorized.

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** Zero Trust is often mistakenly treated as a firewall replacement or a single vendor solution. It's an *architectural philosophy* that requires changes across identity, networking, and application layers.

A few lessons from real implementations:

- **Start with identity** — it's the new perimeter. Get MFA and conditional access policies right before anything else.
- **Service-to-service auth is frequently overlooked.** Internal APIs calling each other still need mutual TLS (mTLS) or token-based auth.
- **Logging is non-negotiable.** Zero Trust only works if you can detect anomalies — ship logs to a SIEM from day one.
- Expect friction during rollout; **user education** reduces helpdesk tickets significantly.
