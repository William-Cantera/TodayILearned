# TIL: Zero Trust Architecture Principles

*Date: 2026-11-08*

## Summary / Problem Statement

Traditional network security models operate on a "castle and moat" assumption — once inside the perimeter, users and devices are implicitly trusted. This breaks down in modern environments with remote workers, cloud services, and SaaS apps where **there is no meaningful perimeter**. Zero Trust Architecture (ZTA) addresses this by eliminating implicit trust entirely.

---

## Key Concepts & Technical Details

Zero Trust is built on one core principle: **"Never trust, always verify."** Every request — regardless of origin — must be authenticated, authorized, and continuously validated.

**Core pillars:**

- **Identity as the new perimeter** — Users, devices, and services must authenticate strongly (MFA, certificates, workload identity) before accessing any resource.
- **Least privilege access** — Grant only the minimum permissions required, scoped to the task and time window. Use just-in-time (JIT) provisioning where possible.
- **Micro-segmentation** — Divide the network into small zones. A compromised workload in one segment cannot freely reach others.
- **Assume breach** — Design systems expecting adversaries are already inside. Prioritize detection, logging, and lateral movement prevention.
- **Device health verification** — Access decisions factor in device posture (patch level, EDR status, compliance) not just user identity.
- **Continuous validation** — Trust is not a one-time handshake. Sessions are re-evaluated based on risk signals (anomalous location, behavior changes).

**Common implementation components:**

- Identity Providers (IdP): Okta, Azure AD, Google Workspace
- Policy Enforcement Points (PEP): proxies, API gateways, service meshes
- SIEM/SOAR for continuous monitoring

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** ZTA is a strategy, not a product. Vendors love to slap "Zero Trust" on everything — a single tool won't get you there.

Start with **identity hygiene**: enforce MFA, audit service accounts, and eliminate shared credentials. These deliver immediate value before tackling network segmentation.

Also watch out for **over-permissive service-to-service auth** — internal APIs are a common blind spot. Treat them as untrusted external calls and enforce mTLS or token-based auth between microservices from day one.
