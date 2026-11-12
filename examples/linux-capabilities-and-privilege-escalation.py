"""
Today I Learned Example: Linux Capabilities and Privilege Escalation
Date: 2026-11-11
"""

#!/usr/bin/env python3
# Linux Capabilities and Privilege Escalation
# ============================================
# Linux capabilities divide root privileges into distinct units that can be
# independently granted to processes/files. This is more secure than full root
# because it follows the principle of least privilege.
#
# Common capabilities:
#   CAP_NET_BIND_SERVICE - bind to ports below 1024
#   CAP_NET_RAW          - use raw sockets (ping, packet sniffing)
#   CAP_SYS_ADMIN        - broad admin operations (dangerous!)
#   CAP_SETUID/SETGID    - change process UIDs/GIDs
#   CAP_DAC_OVERRIDE     - bypass file read/write/execute permission checks
#   CAP_CHOWN            - change file ownership
#
# Privilege escalation risk: If a binary has dangerous capabilities set
# (e.g., python3 with cap_setuid), an attacker can escalate to root.
# Example attack: python3 with cap_setuid+ep -> os.setuid(0) -> root shell

import os
import sys
import stat
import subprocess
import pwd
import grp

def get_current_user_info():
    """Display current user and group information."""
    uid = os.getuid()
    gid = os.getgid()
    euid = os.geteuid()
    egid = os.getegid()
    username = pwd.getpwuid(uid).pw_name
    print(f"[*] Current User  : {username} (UID={uid}, GID={gid})")
    print(f"[*] Effective IDs : EUID={euid}, EGID={egid}")
    print(f"[*] Running as root: {euid == 0}")

def check_capabilities_on_file(filepath):
    """
    Use 'getcap' to read capabilities set on a specific file.
    Capabilities on executables allow non-root users to perform
    privileged operations. This is a common misconfiguration to audit.
    """
    print(f"\n[*] Checking capabilities on: {filepath}")
    try:
        result = subprocess.run(
            ["getcap", filepath],
            capture_output=True, text=True
        )
        output = result.stdout.strip()
        print(f"    Capabilities: {output if output else 'none'}")
        # Dangerous capability combinations to watch for:
        if "cap_setuid" in output or "cap_setgid" in output:
            print("    [!] DANGER: cap_setuid/cap_setgid found - privilege escalation possible!")
        if "cap_sys_admin" in output:
            print("    [!] DANGER: cap_sys_admin found - near-root access!")
        if "cap_dac_override" in output:
            print("    [!] DANGER: cap_dac_override found - can bypass file permissions!")
    except FileNotFoundError:
        print("    [!] 'getcap' not found. Install libcap2-bin: sudo apt install libcap2-bin")

def enumerate_capabilities_system_wide():
    """
    Scan common binary locations for files with capabilities set.
    This is a key privilege escalation enumeration technique.
    Best practice for defenders: audit with 'getcap -r / 2>/dev/null'
    """
    print("\n[*] Enumerating capabilities system-wide (requires getcap)...")
    try:
        result = subprocess.run(
            ["getcap", "-r", "/usr/bin", "/usr/sbin", "/bin", "/sbin"],
            capture_output=True, text=True
        )
        lines = result.stdout.strip().splitlines()
        if lines:
            print("    Files with capabilities:")
            for line in lines:
                print(f"      {line}")
                # Flag high-risk capabilities
                if any(c in line for c in ["cap_setuid", "cap_sys_admin", "cap_net_raw"]):
                    print(f"      [!] Review this entry for potential misuse!")
        else:
            print("    No capabilities found in common paths.")
    except FileNotFoundError:
        print("    [!] 'getcap' not found.")

def demonstrate_privilege_escalation_concept():
    """
    Demonstrates what an attacker would do IF python3 had cap_setuid.
    This is educational - shows WHY granting cap_setuid to interpreters is dangerous.
    
    To test (in a safe VM only!):
      sudo setcap cap_setuid+ep /usr/bin/python3
      python3 this_script.py
      sudo setcap -r /usr/bin/python3  # Remove afterwards!
    """
    print("\n[*] Privilege Escalation Concept Demo:")
    print("    If this Python binary had 'cap_setuid',
