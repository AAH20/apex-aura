"""
GPUDirect RoCEv2 RDMA Zero-Copy Receiver.
Streams incoming binary frames directly into POSIX shared memory ring buffers without host CPU intervention.
"""

from typing import Optional
from core.shm_ring import ShmRingBuffer
from dpu.packet_parser import TSSPPacketParser
from core.types import IngressPacket


class RDMARoCEReceiver:
    """
    Simulates / interfaces with libibverbs / DOCA RDMA zero-copy receiver.
    Pushes directly to ShmRingBuffer.
    """

    def __init__(self, ring_buffer: ShmRingBuffer):
        self.ring = ring_buffer

    def ingest_frame(self, packet: IngressPacket) -> bool:
        encoded_bytes = TSSPPacketParser.encode(packet)
        return self.ring.write(encoded_bytes)

    def poll_next_packet(self) -> Optional[IngressPacket]:
        raw_bytes = self.ring.read()
        if not raw_bytes:
            return None
        return TSSPPacketParser.decode(raw_bytes)
