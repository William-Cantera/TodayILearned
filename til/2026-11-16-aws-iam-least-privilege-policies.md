# TIL: AWS IAM Least Privilege Policies

*Date: 2026-11-16*

## Summary / Problem Statement

Granting overly broad IAM permissions (like `"Action": "*"` or attaching `AdministratorAccess`) is one of the most common — and dangerous — misconfigurations in AWS. When a compromised credential has unrestricted access, the blast radius is enormous. Least privilege means giving an identity **only the permissions it needs to do its job, nothing more**.

---

## Key Concepts & Technical Details

- **Least Privilege Principle**: Every IAM user, role, or service should operate with the minimum set of permissions required for its specific task.

- **Policy Types to Know**:
  - **AWS Managed Policies** — Convenient but often too broad (e.g., `AmazonS3FullAccess` grants access to *all* buckets).
  - **Customer Managed Policies** — Preferred for production; scoped to exact resources and actions.
  - **Inline Policies** — Tightly coupled to a single identity; useful for strict one-off permissions.

- **Resource-Level Scoping**: Always specify the `Resource` ARN instead of `"Resource": "*"` where the service supports it.
  ```json
  "Resource": "arn:aws:s3:::my-app-bucket/*"
  ```

- **Condition Keys**: Add guardrails using `Condition` blocks — restrict by IP, MFA status, request time, or tag values.

- **IAM Access Analyzer**: AWS's built-in tool that flags unused permissions and external access exposure. Run it regularly.

- **Permission Boundaries**: A powerful but underused feature — they cap the *maximum* permissions a role can ever have, even if broader policies are attached later.

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha**: A Lambda function given `s3:*` "just to be safe" during development often makes it into production unchanged. If that function is ever exploited, an attacker can exfiltrate or delete every bucket in the account.

**What to do instead**:
- Start with **zero permissions** and add only what's needed.
- Use the **IAM Policy Simulator** to test before deploying.
- Audit with `aws iam generate-service-last-accessed-details` to identify and remove permissions that haven't been used in 90+ days.
- Enforce least privilege reviews as part of your **PR/code review checklist**.

Small permission scopes are cheap to write and invaluable during an incident.
