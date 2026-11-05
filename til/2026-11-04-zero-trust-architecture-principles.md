# TIL: Zero Trust Architecture Principles

*Date: 2026-11-04*

## Summary / Problem Statement

Traditional network security models operate on the assumption that everything inside the corporate perimeter can be trusted. This "castle and moat" approach fails catastrophically once an attacker breaches the perimeter — they can move laterally with little resistance. Zero Trust Architecture (ZTA) was designed to eliminate this implicit trust entirely.

---

## Key Concepts & Technical Details

Zero Trust is built on one core principle: **"Never trust, always verify."** Every request — regardless of origin — must be authenticated, authorized, and continuously validated.

**Core pillars of ZTA:**

- **Identity-Centric Access** — Users, devices, and services must authenticate strongly (MFA, certificates, OIDC/OAuth2) before accessing any resource
- **Least Privilege Access** — Grant only the minimum permissions required for a specific task, scoped as tightly as possible (time-bound, resource-bound)
- **Micro-Segmentation** — Divide the network into small, isolated zones. A breach in one segment doesn't automatically expose others
- **Continuous Verification** — Trust is not a one-time gate. Sessions are re-evaluated based on context: device health, location, behavior anomalies
- **Assume Breach Mentality** — Design systems expecting that attackers are already inside; focus on detection, containment, and blast radius reduction
- **Encrypted Communication** — All traffic, even internal east-west traffic, should be encrypted (mTLS is common in service meshes like Istio)

**Key technologies often associated with ZTA:**
- Identity Providers (Okta, Azure AD)
- Service meshes (Istio, Linkerd)
- Software-Defined Perimeter (SDP) / ZTNA solutions (Cloudflare Access, Zscaler)
- Policy engines (Open Policy Agent / OPA)

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** Zero Trust is a *strategy*, not a product. Vendors love to slap "Zero Trust" on everything — don't let marketing drive architecture decisions.

Start incrementally: enforce MFA everywhere first, then tackle service-to-service auth with mTLS, then layer in micro-segmentation. Trying to implement everything at once leads to operational paralysis.

Also — overly aggressive least-privilege policies without proper tooling (e.g., dynamic secrets via HashiCorp Vault) will frustrate developers and cause teams to create dangerous workarounds. Culture and tooling must evolve together.
