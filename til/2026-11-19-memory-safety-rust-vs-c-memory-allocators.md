# TIL: Memory Safety: Rust vs C Memory Allocators

*Date: 2026-11-19*

## Summary / Problem Statement

When writing systems-level code, how memory is allocated and freed has direct consequences on security and stability. C gives you full control — and full responsibility. Rust enforces safety guarantees at compile time, fundamentally changing how allocator errors manifest (or don't).

---

## Key Concepts & Technical Details

**C Memory Allocator (glibc `malloc`/`free`)**

- Memory is manually managed; the programmer calls `malloc()`, `calloc()`, `realloc()`, and `free()`
- The allocator maintains metadata (chunk headers, free lists) adjacent to heap memory
- Common failure modes:
  - **Use-after-free**: accessing memory after calling `free()`
  - **Double-free**: calling `free()` twice corrupts allocator internals
  - **Heap overflow**: writing past an allocated buffer can overwrite allocator metadata, enabling exploits
- Tools like Valgrind, AddressSanitizer, or custom allocators (jemalloc, tcmalloc) are used to *detect* these issues at runtime

**Rust Memory Allocator**

- Rust uses the same underlying allocator (typically `jemalloc` or the system allocator) but wraps it in ownership semantics enforced by the **borrow checker**
- Memory is freed automatically when the owning variable goes out of scope (`Drop` trait)
- Key guarantees at **compile time**:
  - **No use-after-free**: the borrow checker invalidates references after a move or drop
  - **No double-free**: only one owner can exist at a time
  - **No data races**: mutable aliasing is statically forbidden
- Unsafe blocks (`unsafe {}`) opt out of these guarantees — this is where allocator bugs *can* still occur in Rust

---

## Practical Takeaway / Real-world Gotcha

> Just because Rust uses a safe allocator wrapper doesn't mean allocator bugs are impossible — they're just *contained*.

- Any `unsafe` code interacting with raw pointers (`*mut T`) or FFI can introduce classic C-style heap corruption
- When auditing Rust codebases, focus your security review on every `unsafe` block — that's where the C-like risk re-enters
- In C, **always pair allocations with a single, clearly owned `free()`** and consider using static analysis (e.g., `clang --analyze`) as a baseline safety net
