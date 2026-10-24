# TIL: AWS IAM Least Privilege Policies

*Date: 2026-10-23*

## Summary / Problem Statement

Granting overly broad IAM permissions (e.g., `"Action": "*"` or `"Resource": "*"`) is one of the most common AWS security mistakes. When a role or user is compromised, excessive permissions dramatically increase the blast radius. Least privilege means granting **only the permissions required to perform a specific task — nothing more**.

---

## Key Concepts & Technical Details

- **Least Privilege Principle**: Every IAM identity should have the minimum set of permissions needed for its intended function.

- **Policy Evaluation Logic**: AWS evaluates policies using an explicit **Deny > Allow** model. An explicit `Deny` always wins, even if an `Allow` exists elsewhere.

- **Permission Boundaries**: A permission boundary is an advanced IAM feature that sets the *maximum* permissions an identity can have, regardless of what their attached policies allow. Useful for delegating IAM management safely.

- **Condition Keys**: Narrow permissions further using condition keys like `aws:SourceIp`, `aws:RequestedRegion`, or `s3:prefix` to restrict *when* and *where* actions are valid.

- **Scoped Resource ARNs**: Instead of `"Resource": "*"`, specify exact ARNs:
  ```json
  "Resource": "arn:aws:s3:::my-bucket/uploads/*"
  ```

- **IAM Access Analyzer**: AWS-native tool that generates least-privilege policies based on **actual CloudTrail activity** over a defined period. Invaluable for right-sizing permissions on existing roles.

- **AWS Managed vs. Customer Managed Policies**: Prefer customer-managed policies for production workloads — AWS-managed policies are broad by design and often grant more than needed.

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha**: IAM Access Analyzer policy generation only reflects activity captured in CloudTrail during the selected window. If a code path runs infrequently (e.g., a quarterly report job), its required permissions may be **missing from the generated policy**, causing silent failures in production.

**Actionable steps:**
- Start with `ReadOnly` or scoped policies, then expand based on observed failures.
- Run Access Analyzer over a **90-day window** to capture edge-case code paths.
- Enforce SCPs at the AWS Organizations level as a backstop against privilege escalation.
- Audit unused permissions regularly using IAM's **last accessed data**.
