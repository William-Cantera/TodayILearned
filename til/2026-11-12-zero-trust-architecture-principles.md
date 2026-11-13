# TIL: Zero Trust Architecture Principles

*Date: 2026-11-12*

## Summary / Problem Statement

Traditional network security relied on a "castle-and-moat" model: once inside the perimeter, users and devices were implicitly trusted. This breaks down in modern environments with cloud workloads, remote employees, and SaaS apps — where there *is* no clear perimeter. Zero Trust Architecture (ZTA) addresses this by eliminating implicit trust entirely.

---

## Key Concepts & Technical Details

Zero Trust is built on one core principle: **never trust, always verify** — regardless of whether a request originates inside or outside the network.

**The three pillars:**

- **Verify explicitly** — Authenticate and authorize every request using all available signals: identity, location, device health, and behavior.
- **Use least-privilege access** — Grant only the minimum permissions needed, enforced via just-in-time (JIT) and just-enough-access (JEA) policies.
- **Assume breach** — Design systems expecting adversaries are already inside. Segment networks, encrypt traffic end-to-end, and log everything.

**Key technical components:**

- **Identity Provider (IdP):** The cornerstone of ZTA. Multi-factor authentication (MFA) and conditional access policies gate every login.
- **Micro-segmentation:** Divides the network into small zones so lateral movement is contained even after a breach.
- **Device posture checks:** Requests from unmanaged or non-compliant devices are denied or sandboxed, even with valid credentials.
- **Continuous validation:** Trust is not a one-time check — sessions are re-evaluated based on risk signals (e.g., anomalous location mid-session).

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** Zero Trust is a *strategy*, not a product. Vendors love to slap "Zero Trust" on firewalls and VPNs, but purchasing a single tool won't get you there.

The real work is **policy definition** — mapping who accesses what, under which conditions, and why. Start with your most sensitive resources and work outward.

- Enforce MFA everywhere before anything else — it's the highest-ROI first step.
- Audit service-to-service authentication too; machine identities are just as exploitable as human ones.
- Expect friction during rollout; involve end users early to avoid shadow-IT workarounds that undermine the entire model.
