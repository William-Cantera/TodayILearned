# TIL: Zero Trust Architecture Principles

*Date: 2026-10-30*

## Summary / Problem Statement

Traditional network security relied on a "castle and moat" model — once inside the perimeter, users and devices were implicitly trusted. This assumption breaks down in modern environments with remote work, cloud services, and insider threats. **Zero Trust Architecture (ZTA)** eliminates implicit trust entirely, requiring continuous verification regardless of network location.

---

## Key Concepts & Technical Details

Zero Trust is built on three core principles:

- **Never Trust, Always Verify**
  Every access request is authenticated and authorized, whether it originates inside or outside the corporate network. No session is trusted by default.

- **Least Privilege Access**
  Users, services, and devices receive only the minimum permissions needed for a specific task. This limits blast radius if credentials are compromised.

- **Assume Breach**
  Systems are designed with the assumption that a breach has already occurred or will occur. This drives micro-segmentation, end-to-end encryption, and comprehensive logging.

**Technical building blocks typically include:**

- **Identity Provider (IdP):** Centralized authentication via OIDC/SAML (e.g., Okta, Azure AD)
- **Multi-Factor Authentication (MFA):** Mandatory for all access paths
- **Micro-segmentation:** Network zones isolated at a granular level, limiting lateral movement
- **Device Posture Checks:** Validating OS patch level, disk encryption, and compliance before granting access
- **Continuous Authorization:** Short-lived tokens and session re-evaluation rather than long-lived credentials
- **Service Mesh / mTLS:** Mutual TLS between services ensures machine-to-machine trust is also explicit

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** Zero Trust is a *strategy*, not a product. Vendors will market single tools as "Zero Trust solutions," but true ZTA requires coordinating identity, device, network, and application layers together.

A common mistake is enforcing MFA at the perimeter but issuing long-lived session tokens internally — an attacker who steals a token bypasses all that friction entirely.

**Start here:** Audit your service-to-service calls. Internal APIs trusting each other without authentication is one of the most overlooked gaps in real deployments.
