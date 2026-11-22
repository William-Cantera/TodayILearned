"""
Today I Learned Example: Memory Safety: Rust vs C Memory Allocators
Date: 2026-11-21
"""

# Memory Safety: Rust vs C Memory Allocators
# This script demonstrates memory safety concepts by simulating how
# Rust's ownership model prevents common C memory errors like:
# - Use-after-free
# - Double-free
# - Memory leaks
# - Buffer overflows
# We use Python to MODEL these concepts (Python itself is memory-safe)

import ctypes
import sys
from collections import defaultdict

# --- Simulating C-style manual memory management (UNSAFE patterns) ---

class CStyleAllocator:
    """
    Simulates C malloc/free behavior.
    Tracks allocations to expose common bugs.
    Best practice in C: always free what you malloc, never free twice.
    """
    def __init__(self):
        self.heap = {}          # address -> (data, is_freed)
        self.next_addr = 1000   # simulated memory address
        self.leak_log = []

    def malloc(self, size):
        """Allocate a buffer of given size (like C malloc)."""
        addr = self.next_addr
        self.heap[addr] = [0] * size   # uninitialized (zeros here for clarity)
        self.next_addr += size + 8     # simulate alignment padding
        print(f"  [C malloc]  Allocated {size} bytes at addr={addr}")
        return addr

    def free(self, addr):
        """Free memory at address (like C free)."""
        if addr not in self.heap:
            # DOUBLE-FREE BUG: freeing memory not allocated or already freed
            raise RuntimeError(f"  [C BUG] Double-free or invalid free at addr={addr}!")
        del self.heap[addr]
        print(f"  [C free]    Freed memory at addr={addr}")
        # Dangling pointer: caller still holds 'addr' value but memory is gone!

    def write(self, addr, index, value):
        """Write to allocated buffer (no bounds checking in C!)."""
        if addr not in self.heap:
            raise RuntimeError(f"  [C BUG] Use-after-free: writing to freed addr={addr}!")
        buf = self.heap[addr]
        if index >= len(buf):
            # BUFFER OVERFLOW: C does NOT check this — undefined behavior!
            raise RuntimeError(f"  [C BUG] Buffer overflow: index {index} >= size {len(buf)}!")
        buf[index] = value

    def check_leaks(self):
        if self.heap:
            print(f"  [C BUG] Memory LEAK detected! {len(self.heap)} allocation(s) never freed.")
        else:
            print("  [C] No leaks detected.")


# --- Simulating Rust-style ownership and borrow checker (SAFE patterns) ---

class RustOwnershipModel:
    """
    Simulates Rust's ownership: one owner, move semantics, automatic drop.
    When owner goes out of scope, memory is freed automatically (RAII).
    Best practice: design APIs so ownership transfer is explicit.
    """
    def __init__(self):
        self.owned = {}   # variable_name -> data

    def allocate(self, name, data):
        """Rust: let name = Box::new(data) — owner is 'name'."""
        self.owned[name] = data
        print(f"  [Rust alloc] '{name}' owns {data}")

    def move_ownership(self, from_name, to_name):
        """Rust: let to_name = from_name  — moves ownership, from_name is invalid."""
        if from_name not in self.owned:
            raise RuntimeError(f"  [Rust BUG] Use of moved value: '{from_name}' no longer owns data!")
        self.owned[to_name] = self.owned.pop(from_name)
        print(f"  [Rust move]  Ownership moved from '{from_name}' to '{to_name}'")

    def drop(self, name):
        """Rust: explicit drop(name) or end of scope — memory freed immediately."""
        if name not in self.owned:
            raise RuntimeError(f"  [Rust BUG] Cannot drop '{name}': already dropped or moved!")
        del self.owned[name]
        print(f"  [Rust drop]  '{name}' dropped, memory freed automatically (no leak possible)")

    def use_value(self, name):
        """Access value — Rust borrow checker ensures it's still valid."""
        if name not in self.owned:
            raise RuntimeError(f"  [Rust ERROR] Borrow of moved/dropped value: '{name}'!")
        print(f"  [Rust read]  '{name}' safely read: {self.owned[name]}")


# === DEMO ===
print("=" * 55)
print("  C-STYLE ALLOCATOR: demonstrating common memory bugs")
print("
