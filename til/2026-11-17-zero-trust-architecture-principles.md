# TIL: Zero Trust Architecture Principles

*Date: 2026-11-17*

## Summary / Problem Statement

Traditional network security relied on a "castle and moat" model — once inside the perimeter, users and devices were implicitly trusted. This assumption breaks down in modern environments with cloud workloads, remote employees, and third-party integrations. A single compromised credential can give an attacker unrestricted lateral movement across the entire network.

**Zero Trust Architecture (ZTA)** flips this model entirely: *never trust, always verify* — regardless of whether a request originates inside or outside the network perimeter.

---

## Key Concepts & Technical Details

- **Verify Explicitly**: Every access request must be authenticated and authorized using all available signals — identity, device health, location, and behavioral context.

- **Least Privilege Access**: Users and services receive only the minimum permissions needed for a specific task, scoped as tightly as possible (time-bound, resource-bound).

- **Assume Breach**: Design systems as if an attacker is already inside. This drives micro-segmentation, end-to-end encryption, and comprehensive logging.

- **Core Pillars** (per NIST SP 800-207):
  - **Identity** — Strong MFA, continuous validation
  - **Device** — Posture checks before granting access
  - **Network** — Micro-segmentation, encrypted traffic (mTLS)
  - **Application** — Per-request authorization, not per-session
  - **Data** — Classification, DLP policies, encryption at rest

- **Policy Decision Point (PDP) / Policy Enforcement Point (PEP)**: The architectural split where a central engine *decides* access and a gateway *enforces* it — keeping logic decoupled from infrastructure.

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha**: Zero Trust is a *strategy*, not a product. Vendors love to slap the label on VPNs or firewalls — that's not ZTA.

- Start with **identity as the new perimeter** — invest in a solid IdP with conditional access policies before touching network segmentation.
- Inventory your service-to-service calls early; **lateral east-west traffic** is often the most overlooked attack surface.
- Logging *everything* is essential, but plan for the storage and SIEM costs — ZTA dramatically increases telemetry volume.
- Incremental adoption wins: migrate one workload or user group at a time rather than attempting a big-bang rollout.
