# TIL: Zero Trust Architecture Principles

*Date: 2026-10-21*

## Summary / Problem Statement

Traditional network security operated on a "castle-and-moat" model: once inside the perimeter, users and devices were implicitly trusted. This breaks down catastrophically in modern environments with remote workers, cloud services, and sophisticated lateral-movement attacks. **Zero Trust Architecture (ZTA)** eliminates implicit trust entirely — every request must be verified, regardless of origin.

---

## Key Concepts & Technical Details

Zero Trust is built on three core tenets:

- **Never trust, always verify** — Every access request is authenticated and authorized as if it originates from an untrusted network, even internal ones.
- **Least privilege access** — Users, services, and devices receive only the minimum permissions required for their specific task, scoped as tightly as possible.
- **Assume breach** — Design systems expecting that a compromise has already occurred; limit blast radius through segmentation and monitoring.

Key technical components that enable ZTA:

- **Identity as the new perimeter** — Strong identity verification via MFA, OIDC/OAuth 2.0, and short-lived tokens (e.g., JWTs with tight expiry).
- **Micro-segmentation** — Network policies that isolate workloads so a compromised service can't freely reach others (e.g., Kubernetes `NetworkPolicy`, AWS Security Groups).
- **Continuous validation** — Posture checks on devices (OS patch level, EDR status) re-evaluated at runtime, not just at login.
- **Mutual TLS (mTLS)** — Service-to-service communication authenticated on *both* sides, commonly enforced via a service mesh like Istio or Linkerd.

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** Zero Trust is a *strategy*, not a product. Vendors love slapping "Zero Trust" on anything — a VPN replacement is not ZTA by itself.

When implementing ZTA incrementally:

- Start with **identity and MFA** — it yields the highest immediate risk reduction.
- Audit service-to-service calls early; hardcoded credentials hiding in internal APIs are a common nasty surprise.
- Expect friction. Short-lived credentials and continuous posture checks *will* break legacy workflows that assumed persistent sessions.

Zero Trust is a journey measured in maturity levels, not a switch you flip.
