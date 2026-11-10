"""
Today I Learned Example: Wireshark TCP Stream Reassembly
Date: 2026-11-09
"""

# Wireshark TCP Stream Reassembly - Educational Demonstration
# This script simulates how Wireshark reassembles TCP streams from individual packets.
#
# TCP Stream Reassembly is the process of reconstructing the original application-layer
# data from a sequence of TCP segments. TCP is a stream-oriented protocol, meaning data
# can be split across multiple packets or arrive out of order. Wireshark (and this demo)
# uses sequence numbers to reorder and reassemble the complete payload.
#
# WHEN TO USE: Network forensics, protocol analysis, debugging client-server apps,
# extracting files/data from packet captures, intrusion detection.
#
# BEST PRACTICES:
# - Always track sequence numbers, not just packet order
# - Handle overlapping segments (retransmissions) gracefully
# - Set a buffer limit to prevent memory exhaustion attacks
# - Validate sequence number wrap-around (32-bit rollover)

import struct
import io
from collections import namedtuple

# Simulate a TCP segment with key header fields
TCPSegment = namedtuple('TCPSegment', ['seq_num', 'payload'])

class TCPStreamReassembler:
    """
    Simulates Wireshark-style TCP stream reassembly.
    Buffers out-of-order segments and delivers them in correct sequence order.
    """

    MAX_BUFFER_BYTES = 1024 * 1024  # 1MB safety limit (prevents memory exhaustion)

    def __init__(self, initial_seq: int):
        # The next expected sequence number (like Wireshark's 'next expected seq')
        self.next_seq = initial_seq
        # Buffer for out-of-order segments: {seq_num: payload_bytes}
        self.out_of_order = {}
        # Reassembled stream output
        self.stream = io.BytesIO()
        self.total_buffered = 0

    def add_segment(self, segment: TCPSegment) -> bytes:
        """
        Process an incoming TCP segment. Returns any newly deliverable data.
        This mirrors Wireshark's segment reassembly logic.
        """
        delivered = b""

        # CASE 1: Duplicate / already-seen segment (retransmission) - discard it
        if segment.seq_num < self.next_seq:
            print(f"  [DISCARD] Retransmission or duplicate at seq={segment.seq_num}")
            return delivered

        # CASE 2: In-order segment - deliver immediately
        if segment.seq_num == self.next_seq:
            self.stream.write(segment.payload)
            delivered += segment.payload
            self.next_seq += len(segment.payload)
            print(f"  [IN-ORDER] seq={segment.seq_num}, len={len(segment.payload)}, next_seq={self.next_seq}")

            # Check if buffered segments can now be delivered (fill the gap)
            while self.next_seq in self.out_of_order:
                buffered_payload = self.out_of_order.pop(self.next_seq)
                self.stream.write(buffered_payload)
                delivered += buffered_payload
                self.total_buffered -= len(buffered_payload)
                print(f"  [FLUSHED] buffered seq={self.next_seq}, len={len(buffered_payload)}")
                self.next_seq += len(buffered_payload)

        # CASE 3: Out-of-order segment - buffer it until the gap is filled
        else:
            if self.total_buffered + len(segment.payload) > self.MAX_BUFFER_BYTES:
                print(f"  [DROP] Buffer limit exceeded at seq={segment.seq_num}")
                return delivered
            self.out_of_order[segment.seq_num] = segment.payload
            self.total_buffered += len(segment.payload)
            print(f"  [BUFFERED] Out-of-order seq={segment.seq_num}, waiting for seq={self.next_seq}")

        return delivered

    def get_stream(self) -> bytes:
        """Return the fully reassembled stream data."""
        return self.stream.getvalue()


# --- DEMONSTRATION ---
if __name__ == "__main__":
    print("=== TCP Stream Reassembly Demo ===\n")

    # Simulate an HTTP request split across 4 TCP segments, delivered out of order
    # Initial sequence number (SYN establishes this; here we use 1000)
    reassembler = TCPStreamReassembler(initial_seq=1000)

    # Define segments: (seq_num, data) - simulating out-of-order delivery
    segments = [
        TCPSegment(1000, b"GET /index.html "),   # Arrives first  (in order)
        TCPSegment(1032, b"HTTP/1.1\r\n"),        #
