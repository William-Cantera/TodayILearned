# TIL: AWS IAM Least Privilege Policies

*Date: 2026-10-26*

## Summary / Problem Statement

When working with AWS, it's tempting to attach `AdministratorAccess` or wildcard permissions (`*`) to get things working quickly. This creates serious security risks — over-permissioned roles become a major blast radius if credentials are compromised. Today I revisited how to properly apply **least privilege** principles when writing IAM policies.

---

## Key Concepts & Technical Details

**Least privilege** means granting only the permissions required to perform a specific task — nothing more.

- **IAM Policy Structure**: Every policy is built from `Effect`, `Action`, `Resource`, and optional `Condition` blocks.
- **Wildcards are dangerous**: `"Action": "s3:*"` on `"Resource": "*"` allows *every* S3 operation on *every* bucket — far beyond what most services need.
- **Scope by resource ARN**: Instead of `*`, specify the exact ARN:
  ```json
  "Resource": "arn:aws:s3:::my-app-bucket/*"
  ```
- **Use IAM Access Analyzer**: AWS provides this tool to automatically identify overly permissive policies and suggest tighter alternatives based on actual access patterns (CloudTrail logs).
- **Condition keys add context**: You can restrict actions further using conditions, e.g., enforce MFA or limit to a specific AWS region:
  ```json
  "Condition": { "StringEquals": { "aws:RequestedRegion": "us-east-1" } }
  ```
- **Permission boundaries**: A guardrail that caps the maximum permissions an identity can have, even if broader policies are attached later.

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha**: A Lambda function was given `s3:*` to "keep things simple" during development. When it was accidentally misconfigured, it deleted production data from an unrelated bucket — because the wildcard resource allowed it.

**What to do instead:**

- Start with **AWS managed policies** as a reference, then trim them down.
- Use **IAM Access Analyzer with policy generation** — it reads CloudTrail history and builds a minimal policy from *real* usage.
- Audit regularly; permissions tend to **accumulate over time** as features are added and old ones are never removed.
- Apply the principle early — retrofitting least privilege onto an existing system is significantly harder than building it in from the start.
