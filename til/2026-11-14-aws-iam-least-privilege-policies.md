# TIL: AWS IAM Least Privilege Policies

*Date: 2026-11-14*

## Summary / Problem Statement

When setting up AWS IAM permissions, it's tempting to attach `AdministratorAccess` or wildcard policies (`"Action": "*"`) to get things working quickly. This creates serious security risks — over-permissioned roles become a massive blast radius if credentials are ever compromised.

Least privilege means granting **only the permissions required to perform a specific task**, nothing more.

---

## Key Concepts & Technical Details

- **IAM Policy Evaluation Logic**: AWS denies by default. Permissions must be explicitly granted. An explicit `Deny` always overrides any `Allow`.

- **Wildcards are dangerous at scale**: `"Action": "s3:*"` on `"Resource": "*"` grants full S3 access across *all* buckets in the account — not just the one you intended.

- **Resource-level permissions**: Always scope the `Resource` ARN as tightly as possible:
  ```json
  "Resource": "arn:aws:s3:::my-app-bucket/*"
  ```
  instead of `"Resource": "*"`.

- **IAM Access Analyzer**: AWS provides this tool to automatically identify unused permissions and generate least-privilege policies based on actual CloudTrail activity. Use it to right-size roles over time.

- **Permission Boundaries**: A guardrail mechanism that caps the *maximum* permissions an IAM entity can have, even if broader policies are attached. Useful in multi-team environments.

- **Service Control Policies (SCPs)**: In AWS Organizations, SCPs restrict what's possible at the account level — another layer of defense independent of IAM policies.

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha**: A Lambda function was given `s3:*` during development. Months later, a misconfigured event trigger caused it to accidentally **delete production objects** — a permission it never needed.

**What to do instead:**

- Start with `ReadOnly` managed policies, then add only what breaks.
- Use **IAM Access Analyzer's policy generation** after a dry run in staging — it reads CloudTrail logs and outputs a minimal policy automatically.
- Audit roles quarterly; unused permissions accumulate silently.
- Prefer **roles over long-lived access keys** wherever possible.

Least privilege isn't a one-time setup — it's an ongoing hygiene practice.
