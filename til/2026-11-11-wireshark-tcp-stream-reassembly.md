# TIL: Wireshark TCP Stream Reassembly

*Date: 2026-11-11*

## Summary / Problem Statement

When analyzing network traffic in Wireshark, raw TCP packets rarely tell the whole story. TCP is a streaming protocol — application data is split across multiple segments. Without reassembly, you're reading fragments instead of the full conversation, making it nearly impossible to debug HTTP requests, file transfers, or custom protocol issues.

## Key Concepts & Technical Details

**TCP Stream Reassembly** is Wireshark's ability to stitch together TCP segments in sequence-number order and present the complete application-layer payload.

- **How it works:** Wireshark tracks each TCP flow by its 4-tuple (`src IP`, `src port`, `dst IP`, `dst port`) and uses TCP sequence numbers to reorder and reassemble segments into a coherent byte stream.
- **Follow TCP Stream:** Right-click any TCP packet → *Follow → TCP Stream*. This opens a window showing the full bidirectional conversation, color-coded by direction (client = red, server = blue by default).
- **Reassembly is enabled by default** under *Preferences → Protocols → TCP → "Allow subdissector to reassemble TCP streams"*. Disabling it forces Wireshark to dissect each segment independently.
- **Sequence numbers matter:** If packets are captured out of order or segments are missing, reassembly will stall or produce gaps. Wireshark marks these with `[TCP Previous segment not captured]` or `[TCP Out-Of-Order]` annotations.
- **Desegmentation vs. Reassembly:** *Desegmentation* refers to TCP-layer reconstruction; *reassembly* often refers to the application layer (e.g., HTTP chunked responses being merged). Both are controlled by separate protocol preferences.

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** Reassembly can mask performance problems.

When you *Follow TCP Stream*, Wireshark presents clean, complete data — but the underlying capture may show retransmissions, duplicate ACKs, or out-of-order segments that caused real latency. Always cross-reference the reassembled view with the raw packet list to catch:

- **Retransmissions** inflating transfer time
- **Zero Window** conditions stalling the sender
- **Missing segments** caused by capture drops, not network drops

Use *Statistics → TCP Stream Graphs → Time-Sequence (Stevens)* alongside stream reassembly for a complete picture of TCP health.
