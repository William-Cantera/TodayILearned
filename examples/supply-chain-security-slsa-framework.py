"""
Today I Learned Example: Supply Chain Security: SLSA Framework
Date: 2026-11-27
"""

# Supply Chain Security: SLSA (Supply Levels for Software Artifacts) Framework
# SLSA is a security framework to prevent tampering, improve integrity, and
# secure packages and infrastructure in your software supply chain.
#
# SLSA defines 4 levels of increasing security guarantees:
# Level 1: Provenance exists (build process documented)
# Level 2: Hosted source + build service (signed provenance)
# Level 3: Hardened build platform (non-falsifiable provenance)
# Level 4: Two-party review + hermetic builds
#
# This script demonstrates core SLSA concepts: provenance generation,
# artifact integrity verification, and build metadata tracking.

import hashlib
import json
import os
import time
import hmac
import base64
from datetime import datetime, timezone

# ─── PROVENANCE GENERATION (SLSA Level 1+) ───────────────────────────────────
# Provenance is a verifiable record of how an artifact was built.
# It answers: WHO built it, WHEN, FROM WHAT source, using WHAT process.

def compute_artifact_digest(filepath: str) -> str:
    """Compute SHA-256 digest of an artifact for integrity verification."""
    sha256 = hashlib.sha256()
    # Read in chunks to handle large files efficiently
    content = filepath.encode("utf-8")  # Simulating file content as bytes
    sha256.update(content)
    return f"sha256:{sha256.hexdigest()}"

def generate_provenance(
    artifact_name: str,
    artifact_content: str,
    builder_id: str,
    source_repo: str,
    source_commit: str,
    build_config: dict
) -> dict:
    """
    Generate SLSA provenance document for a software artifact.
    Best practice: Always include digest, builder identity, and source reference.
    """
    # Compute artifact digest — core of supply chain integrity
    digest = hashlib.sha256(artifact_content.encode()).hexdigest()

    provenance = {
        "_type": "https://in-toto.io/Statement/v0.1",
        "predicateType": "https://slsa.dev/provenance/v0.2",
        "subject": [
            {
                "name": artifact_name,
                "digest": {"sha256": digest}
            }
        ],
        "predicate": {
            "builder": {"id": builder_id},
            "buildType": "https://example.com/build@v1",
            "invocation": {
                "configSource": {
                    "uri": source_repo,
                    "digest": {"sha1": source_commit},
                }
            },
            "buildConfig": build_config,
            "metadata": {
                "buildStartedOn": datetime.now(timezone.utc).isoformat(),
                "completeness": {
                    "parameters": True,   # All build params recorded
                    "environment": False, # Env not fully captured (Level 1/2)
                    "materials": True
                },
                "reproducible": False  # Set True only for hermetic builds (Level 4)
            },
            "materials": [
                {"uri": source_repo, "digest": {"sha1": source_commit}}
            ]
        }
    }
    return provenance

# ─── PROVENANCE SIGNING (SLSA Level 2+) ──────────────────────────────────────
# At Level 2+, provenance must be signed to prevent tampering.
# Best practice: Use asymmetric keys in production (e.g., Sigstore/cosign).

SECRET_KEY = b"demo-signing-key-use-asymmetric-in-production"

def sign_provenance(provenance: dict) -> str:
    """Sign provenance using HMAC-SHA256 (use asymmetric signing in production)."""
    payload = json.dumps(provenance, sort_keys=True).encode()
    signature = hmac.new(SECRET_KEY, payload, hashlib.sha256).digest()
    return base64.b64encode(signature).decode()

def verify_provenance(provenance: dict, signature: str) -> bool:
    """Verify provenance signature — critical step before trusting any artifact."""
    expected_sig = sign_provenance(provenance)
    return hmac.compare_digest(expected_sig, signature)  # Constant-time comparison

# ─── SLSA LEVEL EVALUATOR ────────────────────────────────────────────────────

def evaluate_slsa_level(provenance: dict, is_signed: bool, two_party_review: bool) -> int:
    """Determine achieved SLSA level based on provenance properties."""
    pred = provenance.get("predicate", {})
    meta = pred.get("metadata", {})
    level = 0
    if provenance.get("subject") and pred.get("builder"):
        level = 1  # Prov
