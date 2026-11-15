# TIL: Linux Capabilities and Privilege Escalation

*Date: 2026-11-14*

## Summary / Problem Statement

Running processes as root grants unlimited system access — a massive security risk. Linux capabilities offer a more granular alternative, but misconfigured capabilities can silently introduce privilege escalation vectors that are easy to miss during security audits.

---

## Key Concepts & Technical Details

Linux **capabilities** break the all-or-nothing root privilege model into discrete units. Instead of running a binary as root, you grant only the specific privilege it needs.

**Common capabilities:**
- `CAP_NET_BIND_SERVICE` — bind to ports below 1024
- `CAP_SYS_PTRACE` — trace arbitrary processes
- `CAP_DAC_OVERRIDE` — bypass file read/write/execute permission checks
- `CAP_SETUID` — make arbitrary changes to process UIDs

**How to inspect capabilities:**

```bash
# Check capabilities on a specific binary
getcap /usr/bin/python3

# Recursively find all binaries with capabilities set
getcap -r / 2>/dev/null
```

**How capabilities are set:**

```bash
# Grant a capability to a binary
sudo setcap cap_net_bind_service+ep /usr/bin/node

# Remove all capabilities
sudo setcap -r /usr/bin/node
```

The `+ep` flags mean the capability is **effective** and **permitted** for that binary.

**The dangerous pattern — `CAP_SETUID` on an interpreter:**

```bash
# If this exists on your system...
getcap /usr/bin/python3
# python3 = cap_setuid+ep

# An attacker can do:
python3 -c "import os; os.setuid(0); os.system('/bin/bash')"
# Result: root shell
```

Interpreters like Python, Perl, or Ruby with `CAP_SETUID` are essentially equivalent to a SUID root binary.

---

## Practical Takeaway / Real-world Gotcha

> **Capabilities on interpreters or scripting runtimes are almost always a critical misconfiguration.**

- Regularly audit your systems with `getcap -r / 2>/dev/null` — pipe it into your security scanning pipeline
- Prefer capabilities on purpose-built, minimal binaries rather than general-purpose runtimes
- Remember: capabilities survive across container image layers; always verify your final image with `docker run --rm <image> getcap -r /`
- Tools like **LinPEAS** and **GTFOBins** specifically enumerate capability misconfigurations during penetration tests
