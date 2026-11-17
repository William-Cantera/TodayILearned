# TIL: Supply Chain Security: SLSA Framework

*Date: 2026-11-16*

## Summary / Problem Statement

Modern software depends on hundreds of upstream dependencies, build tools, and CI/CD pipelines — any of which can be compromised. The **SolarWinds** and **XZ Utils** attacks demonstrated that tampering can happen at the *build* level, not just the source level. SLSA (Supply-chain Levels for Software Artifacts, pronounced "salsa") is a security framework from Google that provides a concrete, incremental way to harden this entire chain.

---

## Key Concepts & Technical Details

**SLSA defines four trust levels (L1–L4)**, each adding stricter requirements:

- **L1 – Provenance exists**: The build process generates a signed provenance document describing *what* was built, *from what source*, and *how*.
- **L2 – Hosted build service**: Builds run on a hosted, auditable CI system (e.g., GitHub Actions, Google Cloud Build). Provenance is signed by the build platform itself, not just the developer.
- **L3 – Hardened builds**: The build environment is isolated, ephemeral, and parameterized. No human can inject arbitrary inputs mid-build.
- **L4 – Two-party review + hermetic builds**: All source changes require review; builds are fully hermetic (no network access, fully reproducible).

**Key supporting components:**

- **Provenance**: A signed SLSA attestation (often using [in-toto](https://in-toto.io/) format) stored alongside the artifact.
- **Sigstore / `cosign`**: Commonly used tooling to sign and verify SLSA provenance for container images and binaries.
- **SLSA verifier CLI**: Lets consumers validate an artifact's provenance before use.

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha**: Generating provenance at L2 is relatively easy with GitHub Actions' [SLSA Generic Generator](https://github.com/slsa-framework/slsa-github-generator), but **consumers rarely verify it** — making the attestation theater unless verification is enforced in your deployment pipeline (e.g., via OPA policies or admission controllers in Kubernetes).

- Start by targeting **L2** for public releases; it catches the most common attack vectors with modest effort.
- Store attestations in your artifact registry alongside the artifact — don't treat them as an afterthought.
- Wire verification into your CD pipeline, not just your security audits.
