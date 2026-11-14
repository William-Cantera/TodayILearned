# TIL: Memory Safety: Rust vs C Memory Allocators

*Date: 2026-11-13*

## Summary / Problem Statement

Managing memory manually in C is powerful but notoriously error-prone. Rust's ownership model enforces memory safety at compile time, but understanding *how* each language handles allocation under the hood reveals why Rust eliminates entire classes of bugs that plague C programs.

---

## Key Concepts & Technical Details

**C Memory Allocator (`malloc`/`free`)**
- Uses the system allocator (e.g., `ptmalloc2` on Linux, `jemalloc` on FreeBSD) via `libc`
- Developer manually tracks ownership — nothing prevents double-free, use-after-free, or memory leaks
- The compiler has no awareness of object lifetimes; errors surface only at runtime (often silently or as undefined behavior)
- Common pitfalls:
  - `free(ptr)` followed by another `free(ptr)` → heap corruption
  - Accessing `ptr` after `free` → undefined behavior, potential security exploit
  - Forgetting `free` entirely → memory leak

**Rust Memory Allocator**
- Uses `GlobalAlloc` trait; defaults to the system allocator but can be swapped (e.g., `jemalloc` via `tikv-jemallocator`)
- The *borrow checker* enforces ownership rules at **compile time**:
  - Each value has exactly one owner
  - References must not outlive the data they point to
  - Mutable and immutable borrows are mutually exclusive
- `Box<T>`, `Vec<T>`, etc., wrap raw allocations with RAII — memory is freed automatically when the owner goes out of scope
- `unsafe` blocks exist but explicitly opt out of these guarantees, making risk visible in code review

**Custom Allocators**
- C: swap via `malloc`/`free` wrappers or linker tricks — no standard interface
- Rust: implement the `GlobalAlloc` trait and annotate with `#[global_allocator]` — clean, auditable, and type-safe

---

## Practical Takeaway / Real-world Gotcha

> Rust doesn't eliminate allocator bugs by using a *better* allocator — it eliminates them by making **invalid memory states unrepresentable** in safe code.

When integrating Rust with C via FFI, be careful: memory allocated by `malloc` **must** be freed by `free`, not by Rust's allocator. Mixing allocators across the FFI boundary causes silent heap corruption — the exact class of bug Rust was designed to prevent.
