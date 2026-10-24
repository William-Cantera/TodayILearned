"""
Today I Learned Example: AWS IAM Least Privilege Policies
Date: 2026-10-23
"""

# AWS IAM Least Privilege Policy Generator and Analyzer
# This script demonstrates the principle of least privilege for AWS IAM policies.
# Least privilege means granting ONLY the permissions required to perform a task,
# nothing more. This minimizes the attack surface if credentials are compromised.
#
# WHEN TO USE:
# - When creating IAM roles for Lambda functions, EC2 instances, or services
# - When onboarding new users or teams who need limited AWS access
# - When auditing existing policies for over-permissive access
# - As part of a security review or compliance process
#
# BEST PRACTICES:
# 1. Start with zero permissions, add only what is needed
# 2. Use specific resource ARNs instead of wildcards ("*")
# 3. Prefer managed policies for common use cases, inline for specificity
# 4. Regularly audit and rotate/remove unused permissions
# 5. Use conditions (IP, MFA, time) to further restrict access

import json
import copy

# --- Define overly permissive (BAD) policy examples ---
BAD_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "*",           # Wildcard action = full admin access (DANGER)
            "Resource": "*"          # Wildcard resource = applies to everything (DANGER)
        }
    ]
}

# --- Define a least-privilege (GOOD) policy for a Lambda reading from one S3 bucket ---
GOOD_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowS3ReadOnSpecificBucket",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",      # Only read objects
                "s3:ListBucket"      # Only list objects in the bucket
            ],
            "Resource": [
                "arn:aws:s3:::my-app-data-bucket",        # The bucket itself
                "arn:aws:s3:::my-app-data-bucket/*"       # Objects inside the bucket
            ],
            "Condition": {
                "StringEquals": {
                    "aws:RequestedRegion": "us-east-1"    # Restrict to one region
                }
            }
        },
        {
            "Sid": "AllowCloudWatchLogging",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"   # Only log writing, no deletion or reading others' logs
            ],
            "Resource": "arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/my-function:*"
        }
    ]
}

def analyze_policy(policy: dict, name: str) -> dict:
    """Analyze an IAM policy and flag potential over-permissive statements."""
    findings = []
    for stmt in policy.get("Statement", []):
        actions = stmt.get("Action", [])
        resources = stmt.get("Resource", [])
        # Normalize to lists for uniform processing
        if isinstance(actions, str):
            actions = [actions]
        if isinstance(resources, str):
            resources = [resources]

        if "*" in actions:
            findings.append("CRITICAL: Wildcard action '*' grants full access.")
        if "*" in resources:
            findings.append("WARNING: Wildcard resource '*' applies to ALL resources.")
        if stmt.get("Effect") == "Allow" and not stmt.get("Condition"):
            findings.append("INFO: No Condition block — consider adding IP or MFA constraints.")

    return {"policy_name": name, "findings": findings, "total_issues": len(findings)}

def remediate_policy(policy: dict) -> dict:
    """Demonstrate auto-remediation: replace wildcard actions with a safe placeholder."""
    remediated = copy.deepcopy(policy)
    for stmt in remediated.get("Statement", []):
        if stmt.get("Action") == "*":
            # Replace with a read-only placeholder — in real use, specify exact actions
            stmt["Action"] = ["<REPLACE_WITH_SPECIFIC_ACTIONS>"]
            stmt["Resource"] = ["<REPLACE_WITH_SPECIFIC_RESOURCE_ARN>"]
    return remediated

# --- Run the analysis ---
print("=" * 60)
print("IAM Least Privilege Policy Analyzer")
print("=" * 60)

for policy, label in [(BAD_POLICY, "BAD (Over-permissive)"), (GOOD_POLICY, "GOOD (Least Privilege)")]:
    result = analyze_policy(policy, label)
    print(f"\nPolicy: {result['policy_name']}")
    print(f"Issues Found: {result['total_issues']}")
    for finding in result["
