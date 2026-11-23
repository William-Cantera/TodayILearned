# TIL: Docker Container Escape Vectors

*Date: 2026-11-22*

## Summary / Problem Statement

Running workloads in Docker containers doesn't automatically mean they're isolated from the host. Several well-known **escape vectors** allow a compromised or malicious container to break out and gain access to the underlying host system — a critical concern in multi-tenant and production environments.

---

## Key Concepts & Technical Details

**1. Privileged Containers (`--privileged`)**
- Grants the container nearly all Linux capabilities and full access to host devices.
- A process inside can mount the host filesystem (`/dev/sda`) and read/write host files directly.
- Effectively removes the security boundary between container and host.

**2. Dangerous Volume Mounts**
- Mounting sensitive host paths like `/`, `/etc`, `/var/run/docker.sock` gives containers direct host access.
- The **Docker socket** (`docker.sock`) is especially dangerous — it lets the container spawn new privileged containers, enabling a trivial escape.

**3. Excessive Linux Capabilities**
- Capabilities like `CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, or `CAP_SYS_PTRACE` can be exploited individually without full `--privileged` mode.
- `CAP_SYS_ADMIN` alone allows mounting filesystems, a common escape primitive.

**4. Kernel Exploits & Namespace Weaknesses**
- Containers share the host kernel. An unpatched kernel vulnerability (e.g., Dirty COW, runc CVE-2019-5736) can be exploited from inside a container to gain host root.
- The runc vulnerability allowed overwriting the host `runc` binary via `/proc/self/exe`.

**5. User Namespace Misconfigurations**
- Without user namespace remapping enabled, a container running as `root` (UID 0) maps directly to host root, amplifying any escape impact.

---

## Practical Takeaway / Real-world Gotcha

> **Never mount `/var/run/docker.sock` into application containers in production.** It's a common pattern for CI tooling but is essentially handing the container the keys to the host.

- Run containers as **non-root users** (`USER 1001` in your Dockerfile).
- Use `--cap-drop=ALL` and add back only what's needed.
- Enable **seccomp** and **AppArmor** profiles.
- Regularly patch the host kernel — container security is only as strong as the kernel underneath.
- Audit with tools like **Trivy**, **Falco**, or **docker-bench-security**.
