# TIL: AWS IAM Least Privilege Policies

*Date: 2026-10-22*

## Summary / Problem Statement

When working with AWS, it's tempting to attach `AdministratorAccess` or wildcard policies (`"Action": "*"`) to get things working quickly. This creates serious security risks — over-permissioned roles become high-value targets for credential compromise and lateral movement. Least privilege means granting **only the permissions required** to perform a specific task, nothing more.

---

## Key Concepts & Technical Details

**Least Privilege Principle**
- Every IAM identity (user, role, service) should have the *minimum* set of permissions needed to do its job.
- Start with zero permissions and add only what's explicitly required.

**Policy Types to Know**
- **AWS Managed Policies** — Broad, reusable, but often over-permissive (e.g., `AmazonS3FullAccess`).
- **Customer Managed Policies** — Custom JSON you control; preferred for fine-grained access.
- **Inline Policies** — Attached directly to a single identity; useful for strict one-off restrictions.

**Key Policy Elements**
```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::my-bucket/*",
  "Condition": {
    "StringEquals": { "aws:RequestedRegion": "us-east-1" }
  }
}
```
- Use `Condition` blocks to scope permissions further (by region, IP, MFA status, tags).
- Prefer **resource-level ARNs** over `"Resource": "*"` wherever the service supports it.

**Useful Tools**
- **IAM Access Analyzer** — Detects overly permissive policies and unused access.
- **AWS Policy Simulator** — Test policies before deploying them.
- **CloudTrail + IAM Access Advisor** — Identify which permissions are actually being used.

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** Lambda execution roles are a common offender. Developers often attach `AmazonDynamoDBFullAccess` when the function only needs `dynamodb:GetItem` on a single table.

- Audit roles regularly using **IAM Access Advisor** — it shows the last time each service permission was used.
- If a permission hasn't been used in 90 days, it's a candidate for removal.
- Treat IAM policy reviews as part of your **PR review process**, not an afterthought.
