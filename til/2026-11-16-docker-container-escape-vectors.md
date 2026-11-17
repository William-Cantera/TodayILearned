# TIL: Docker Container Escape Vectors

*Date: 2026-11-16*

## Summary / Problem Statement

Running workloads inside Docker containers doesn't automatically guarantee isolation. Several well-known **container escape vectors** allow a compromised or malicious container to break out into the host system — a critical concern for multi-tenant environments and CI/CD pipelines.

---

## Key Concepts & Technical Details

Container escapes typically exploit misconfigurations or overly permissive settings rather than kernel zero-days. The most common vectors include:

- **Privileged Mode (`--privileged`)**
  Grants the container nearly all Linux capabilities and access to host devices. An attacker can mount the host filesystem directly via `/dev` and write to it, achieving full host compromise.

- **Exposed Docker Socket (`-v /var/run/docker.sock:/var/run/docker.sock`)**
  Mounting the Docker daemon socket inside a container gives it the ability to spawn new privileged containers on the host — effectively root access. This is a surprisingly common pattern in CI tooling.

- **Dangerous Capabilities (`--cap-add`)**
  Individual capabilities like `CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, or `CAP_SYS_PTRACE` can be abused. `CAP_SYS_ADMIN` alone enables mounting filesystems, loading kernel modules, and more.

- **Writable Host Path Mounts**
  Mounting sensitive host paths (e.g., `/etc`, `/proc`, `/`) with write access allows direct modification of host configuration files or cgroup settings.

- **Namespace Sharing (`--pid=host`, `--network=host`)**
  Sharing the host PID or network namespace removes process and network isolation, enabling an attacker to inspect or signal host processes.

---

## Practical Takeaway / Real-world Gotcha

> **The Docker socket mount is the most underestimated escape vector in the wild.**

It appears in countless "convenience" setups — Docker-in-Docker patterns, build agents, and monitoring tools — without teams realising it grants equivalent-to-root access.

**Hardening checklist:**

- Never run containers with `--privileged` unless absolutely necessary
- Audit all volume mounts; treat `/var/run/docker.sock` as a root credential
- Use `--cap-drop=ALL` and add back only required capabilities
- Consider rootless Docker or gVisor/Kata Containers for stronger isolation
- Regularly scan `docker inspect` output in production for dangerous flags
