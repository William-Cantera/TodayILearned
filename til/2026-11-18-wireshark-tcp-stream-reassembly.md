# TIL: Wireshark TCP Stream Reassembly

*Date: 2026-11-18*

## Summary / Problem Statement

When analyzing network traffic in Wireshark, raw TCP captures can be overwhelming — individual packets only carry fragments of a conversation. I needed to reconstruct a full HTTP request/response exchange from a pcap file, which led me to discover Wireshark's **TCP Stream Reassembly** feature.

---

## Key Concepts & Technical Details

TCP is a stream-oriented protocol, meaning application data is split across multiple segments before transmission. Wireshark can stitch these segments back together into a human-readable flow.

**How it works:**

- Wireshark tracks TCP sequence numbers to order segments correctly, even if they arrive out of order
- The **Follow TCP Stream** feature (`Right-click → Follow → TCP Stream`) reconstructs the full bidirectional conversation
- Reassembly is handled by the **TCP reassembly engine**, which buffers out-of-order segments and fills gaps before handing data to the application-layer dissector
- You can toggle this behavior under `Edit → Preferences → Protocols → TCP → Allow subdissector to reassemble TCP streams`

**Important display filter behavior:**

- When you follow a stream, Wireshark auto-applies a filter like `tcp.stream eq 4`
- Each unique TCP connection gets its own stream index, assigned in order of the first SYN packet seen
- The stream viewer shows client data in **red** and server data in **blue** by default

**Relevant fields to know:**

- `tcp.reassembled_in` — points to the packet where reassembly completes
- `tcp.segment` — marks a packet as a partial segment contributing to a larger PDU
- `tcp.len` — payload length of the current segment

---

## Practical Takeaway / Real-world Gotcha

> **Gotcha:** Reassembly is enabled by default, which means Wireshark may show an HTTP response dissected in a *later* packet than where the data physically starts. This can confuse latency analysis if you're measuring response times at the packet level.

- Always check `tcp.reassembled_in` when timing seems off
- Disable reassembly temporarily if you need to inspect raw segment boundaries
- For encrypted traffic (TLS), reassembly still works at the TCP layer — you just won't see plaintext without the session keys
