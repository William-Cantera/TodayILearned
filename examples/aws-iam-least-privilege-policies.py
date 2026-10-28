"""
Today I Learned Example: AWS IAM Least Privilege Policies
Date: 2026-10-27
"""

# AWS IAM Least Privilege Policies - Educational Demonstration
# This script demonstrates the concept of least privilege in AWS IAM policies
# using Python's standard library to simulate policy evaluation and generation.
#
# WHAT IS LEAST PRIVILEGE?
# The principle of least privilege means granting only the minimum permissions
# required for a user/service to perform their specific tasks - nothing more.
#
# WHEN TO USE IT:
# - Always. Every IAM user, role, and service should follow this principle.
# - Especially critical for production environments and sensitive data access.
#
# BEST PRACTICES:
# - Start with zero permissions, add only what's needed
# - Avoid wildcard (*) actions and resources where possible
# - Use conditions to further restrict access (time, IP, MFA, etc.)
# - Regularly audit and remove unused permissions

import json
from datetime import datetime

def create_least_privilege_policy(service, actions, resources, conditions=None):
    """
    Generates a minimal IAM policy document.
    Only grants specific actions on specific resources - no wildcards.
    """
    statement = {
        "Effect": "Allow",
        "Action": actions,       # Specific actions only (e.g., "s3:GetObject")
        "Resource": resources,   # Specific ARNs, not "*"
    }
    if conditions:
        statement["Condition"] = conditions  # Extra guardrails

    policy = {
        "Version": "2012-10-17",
        "Statement": [statement]
    }
    return policy

def evaluate_policy_risk(policy):
    """
    Analyzes an IAM policy for common least-privilege violations.
    Returns a risk report highlighting dangerous configurations.
    """
    risks = []
    for stmt in policy.get("Statement", []):
        actions = stmt.get("Action", [])
        resources = stmt.get("Resource", [])
        conditions = stmt.get("Condition", {})

        # RISK: Wildcard action grants ALL permissions on a service or globally
        if "*" in actions or any("*" in a for a in actions):
            risks.append("HIGH: Wildcard action (*) detected - violates least privilege")

        # RISK: Wildcard resource means the action applies to ALL resources
        if resources == "*" or resources == ["*"]:
            risks.append("HIGH: Wildcard resource (*) - scope is too broad")

        # RISK: Admin-level actions should almost never be granted
        admin_actions = {"iam:*", "sts:AssumeRole", "*"}
        if any(a in admin_actions for a in (actions if isinstance(actions, list) else [actions])):
            risks.append("CRITICAL: Admin-level action detected - review immediately")

        # BEST PRACTICE: Conditions add extra security context (MFA, IP, time)
        if not conditions:
            risks.append("INFO: No conditions set - consider adding MFA or IP restrictions")

    return risks if risks else ["PASS: Policy appears to follow least privilege principles"]

# --- DEMONSTRATION ---

print("=" * 60)
print("IAM Least Privilege Policy Demonstration")
print(f"Generated at: {datetime.utcnow().isoformat()}Z")
print("=" * 60)

# GOOD EXAMPLE: Specific S3 read-only access to one bucket prefix
good_policy = create_least_privilege_policy(
    service="s3",
    actions=["s3:GetObject", "s3:ListBucket"],          # Only what's needed
    resources=[
        "arn:aws:s3:::my-app-bucket",
        "arn:aws:s3:::my-app-bucket/reports/*"          # Scoped to a prefix
    ],
    conditions={"Bool": {"aws:MultiFactorAuthPresent": "true"}}  # Require MFA
)

print("\n[GOOD POLICY - Read-only S3 access with MFA condition]")
print(json.dumps(good_policy, indent=2))
print("\nRisk Evaluation:", evaluate_policy_risk(good_policy))

# BAD EXAMPLE: Overly permissive policy (common mistake)
bad_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": "*",        # NEVER do this - grants all AWS actions
        "Resource": "*"       # On all resources - effectively full admin access
    }]
}

print("\n[BAD POLICY - Overly permissive (admin access)]")
print(json.dumps(bad_policy, indent=2))
print("\nRisk Evaluation:", evaluate_policy_risk(bad_policy))

print("\n[KEY TAKEAWAYS]")
takeaways = [
    "1. Always specify exact actions needed (e.g., s3:GetObject, not s3:*)",
    "2. Always scope resources to specific ARNs, never use bare '*'",
    "3. Add
