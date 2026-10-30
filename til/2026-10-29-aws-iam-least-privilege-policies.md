# TIL: AWS IAM Least Privilege Policies

*Date: 2026-10-29*

## Summary / Problem Statement

Granting overly broad IAM permissions (like `*` on all resources) is one of the most common AWS security mistakes. When a Lambda function, EC2 instance, or CI/CD role gets compromised, excessive permissions turn a small incident into a catastrophic breach. The principle of **least privilege** means granting only the exact permissions required — nothing more.

---

## Key Concepts & Technical Details

**Least Privilege** means every IAM identity should have the minimum permissions needed to perform its intended function.

**Key building blocks of an IAM policy:**
- **Effect** – `Allow` or `Deny`
- **Action** – Specific API calls (e.g., `s3:GetObject`, not `s3:*`)
- **Resource** – Specific ARNs, not `"*"` where avoidable
- **Condition** – Optional constraints (e.g., MFA required, specific IP range)

**Example — overly permissive (avoid this):**
```json
{ "Effect": "Allow", "Action": "s3:*", "Resource": "*" }
```

**Example — least privilege (prefer this):**
```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::my-app-bucket/*"
}
```

**Useful tools for scoping permissions down:**
- **IAM Access Analyzer** — identifies unused permissions over a specified period
- **AWS Policy Simulator** — tests what a policy actually allows before deploying
- **CloudTrail + IAM last-accessed data** — reveals which actions an identity actually uses

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** Wildcard resources (`"Resource": "*"`) are sometimes *required* by certain AWS actions (e.g., `ec2:DescribeInstances` doesn't support resource-level restrictions). Always check the [AWS documentation for resource-level permissions](https://docs.aws.amazon.com/service-authorization/latest/reference/) before assuming you can scope everything down.

**Actionable habits:**
- Start with **zero permissions** and add only what breaks
- Use **IAM Access Analyzer** after 30 days of usage to trim unused permissions
- Prefer **resource-based policies** on S3/KMS over broad identity policies
- Never attach `AdministratorAccess` to application roles — reserve it for break-glass scenarios only

Least privilege is not a one-time setup; it requires periodic review as application behavior evolves.
