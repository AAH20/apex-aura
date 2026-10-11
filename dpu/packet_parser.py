"""
TSSP/1.0 Zero-Overhead Binary Packet Decoder.
Decodes high-speed packet frames arriving via RoCEv2 RDMA before OS kernel interrupts.
"""

import struct
from typing import Dict, Any, Tuple
from core.types import IngressPacket


class TSSPPacketParser:
    """
    Decodes binary TSSP frames (Tokenized State Streaming Protocol).
    Magic: 0x54535350 ("TSSP")
    Header: [Magic 4B | Version 2B | Flags 2B | PacketID 16B | Timestamp 8B | PayloadLen 4B]
    """

    MAGIC = b"TSSP"
    HEADER_FMT = "=4sHH16sQI"
    HEADER_SIZE = struct.calcsize(HEADER_FMT)

    @classmethod
    def encode(cls, packet: IngressPacket) -> bytes:
        packet_id_bytes = packet.packet_id.encode("utf-8")[:16].ljust(16, b"\x00")
        payload_bytes = packet.intent.encode("utf-8")
        header = struct.pack(
            cls.HEADER_FMT,
            cls.MAGIC,
            1,  # Version 1
            0,  # Flags
            packet_id_bytes,
            packet.timestamp_ns,
            len(payload_bytes),
        )
        return header + payload_bytes

    @classmethod
    def decode(cls, raw_data: bytes) -> IngressPacket:
        if len(raw_data) < cls.HEADER_SIZE:
            raise ValueError("Buffer too small for TSSP header")

        magic, version, flags, packet_id_raw, timestamp_ns, payload_len = struct.unpack_from(
            cls.HEADER_FMT, raw_data, 0
        )
        if magic != cls.MAGIC:
            raise ValueError(f"Invalid magic: {magic}")

        packet_id = packet_id_raw.decode("utf-8").rstrip("\x00")
        payload = raw_data[cls.HEADER_SIZE: cls.HEADER_SIZE + payload_len].decode("utf-8")

        return IngressPacket(
            packet_id=packet_id,
            timestamp_ns=timestamp_ns,
            source_slice="dpu_roce_v2",
            intent=payload,
        )
