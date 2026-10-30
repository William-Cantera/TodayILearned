# TIL: Linux Capabilities and Privilege Escalation

*Date: 2026-10-29*

## Summary / Problem Statement

While auditing a containerized service, I discovered that a binary had been granted `CAP_NET_BIND_SERVICE` to allow binding to port 80 — but the file capability was set on a Python interpreter, not the specific script. This opened a much wider privilege escalation surface than intended.

Linux capabilities let you grant *slices* of root privilege to processes or binaries without giving full `sudo` access, but misconfiguring them can be just as dangerous.

---

## Key Concepts & Technical Details

**What are Linux Capabilities?**
- The kernel divides traditional root privileges into discrete units (e.g., `CAP_NET_ADMIN`, `CAP_SYS_PTRACE`, `CAP_DAC_OVERRIDE`)
- Capabilities can be assigned to **processes** (at runtime) or **files** (persistent, via `setcap`)

**Dangerous Capabilities to Watch For:**

| Capability | Risk |
|---|---|
| `CAP_DAC_OVERRIDE` | Bypass all file read/write permission checks |
| `CAP_SYS_PTRACE` | Attach to and manipulate any process |
| `CAP_NET_RAW` | Craft raw packets; potential for sniffing |
| `CAP_SETUID` | Change UID — near-equivalent to full root |

**How to Enumerate File Capabilities:**
```bash
# Find all binaries with capabilities set
getcap -r / 2>/dev/null

# Example dangerous output
/usr/bin/python3.10 = cap_setuid+ep
```

The `+ep` suffix means the capability is **effective** and **permitted** — it activates the moment the binary runs, for *any* user.

**Exploitation Pattern:**
```python
# If python has cap_setuid+ep, any user can do:
import os
os.setuid(0)
os.system("/bin/bash")
```

---

## Practical Takeaway / Real-world Gotcha

- **Never set capabilities on generic interpreters** (`python`, `perl`, `ruby`). Apply them to a dedicated, minimal wrapper binary instead.
- Run `getcap -r /` as part of your security audit checklist — it's often overlooked compared to SUID scanning.
- In containers, prefer **dropping all capabilities** with `--cap-drop=ALL` and adding back only what's needed with `--cap-add`.
- Capabilities on files survive across deployments if baked into images, making them easy to forget and hard to spot in CI pipelines.
