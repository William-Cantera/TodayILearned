# TIL: Zero Trust Architecture Principles

*Date: 2026-11-05*

## Summary / Problem Statement

Traditional network security assumed that everything inside a corporate network could be trusted. This "castle and moat" model collapses the moment an attacker gets inside — through phishing, a compromised VPN, or a rogue insider. Zero Trust Architecture (ZTA) challenges this assumption entirely: **trust nothing, verify everything, always**.

---

## Key Concepts & Technical Details

Zero Trust is a security model, not a single product. It rests on a few core principles:

- **Never trust, always verify** — Every request (user, device, service) must authenticate and authorize, regardless of network location. Being "inside the firewall" grants nothing by default.

- **Least privilege access** — Users and services receive only the minimum permissions needed for the task at hand. Permissions are time-bound and scoped narrowly.

- **Assume breach** — Design systems as if an attacker is already present. Segment networks with micro-segmentation so lateral movement is contained.

- **Continuous verification** — Authentication isn't a one-time gate. Session behavior, device health, and context (location, time, risk score) are evaluated continuously.

- **Device trust** — Endpoints must meet a health baseline (patched OS, MDM enrollment, disk encryption) before accessing resources. A valid credential on a compromised device is still a risk.

- **Identity as the new perimeter** — Strong identity providers (IdP), MFA, and short-lived tokens (e.g., OAuth 2.0 + OIDC) replace IP-based trust.

Key enabling technologies: **SPIFFE/SPIRE** for workload identity, **mTLS** for service-to-service auth, **Policy Engines** (OPA, Cedar), and **SASE/SSE** platforms for network enforcement.

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** Zero Trust is an *iterative journey*, not a switch you flip.

A common mistake is purchasing a "Zero Trust" vendor product and calling it done. In practice:

- Legacy apps often can't support mTLS or modern IdPs without a proxy layer.
- Over-restricting access too quickly creates productivity friction and leads to shadow IT.
- Start by **mapping your most sensitive data flows first**, apply controls there, then expand incrementally.

Measure progress by blast radius reduction, not perimeter thickness.
