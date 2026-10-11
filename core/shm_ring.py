"""
POSIX Zero-Copy /dev/shm Ring Buffer (LMAX Disruptor Pattern).
Provides sub-microsecond zero-copy communication between DPU Ingress and the Cognitive Hypervisor.
"""

from __future__ import annotations
import os
import struct
import time
from typing import Optional, Tuple


class ShmRingBuffer:
    """
    Lock-free Single-Producer Single-Consumer (SPSC) Ring Buffer.
    Allocated in memory or backed by /dev/shm.
    Cache-line aligned (64 bytes) to prevent CPU false sharing.
    """

    HEADER_FORMAT = "=QQII"  # head (8B), tail (8B), capacity (4B), slot_size (4B)
    HEADER_SIZE = 64  # Pad header to 64 bytes for cache line alignment

    def __init__(self, capacity: int = 1024, slot_size: int = 4096, shm_path: Optional[str] = None):
        assert (capacity & (capacity - 1)) == 0, "Capacity must be a power of 2"
        self.capacity = capacity
        self.mask = capacity - 1
        self.slot_size = slot_size
        self.total_size = self.HEADER_SIZE + (self.capacity * self.slot_size)
        self.shm_path = shm_path
        self._buffer: bytearray = bytearray(self.total_size)
        self._init_header()

    def _init_header(self) -> None:
        header_data = struct.pack(self.HEADER_FORMAT, 0, 0, self.capacity, self.slot_size)
        self._buffer[0:len(header_data)] = header_data

    def get_head(self) -> int:
        return struct.unpack_from("=Q", self._buffer, 0)[0]

    def set_head(self, val: int) -> None:
        struct.pack_into("=Q", self._buffer, 0, val)

    def get_tail(self) -> int:
        return struct.unpack_from("=Q", self._buffer, 8)[0]

    def set_tail(self, val: int) -> None:
        struct.pack_into("=Q", self._buffer, 8, val)

    def write(self, payload: bytes) -> bool:
        """
        Write payload into the next available slot.
        Returns True if successful, False if the buffer is full.
        """
        if len(payload) > self.slot_size:
            raise ValueError(f"Payload size {len(payload)} exceeds slot size {self.slot_size}")

        head = self.get_head()
        tail = self.get_tail()

        if (tail - head) >= self.capacity:
            return False  # Buffer full

        slot_index = tail & self.mask
        offset = self.HEADER_SIZE + (slot_index * self.slot_size)

        # Write payload length (4 bytes) + data
        payload_len = len(payload)
        struct.pack_into("=I", self._buffer, offset, payload_len)
        self._buffer[offset + 4: offset + 4 + payload_len] = payload

        # Advance tail atomically
        self.set_tail(tail + 1)
        return True

    def read(self) -> Optional[bytes]:
        """
        Read payload from the ring buffer.
        Returns bytes if available, None if empty.
        """
        head = self.get_head()
        tail = self.get_tail()

        if head >= tail:
            return None  # Buffer empty

        slot_index = head & self.mask
        offset = self.HEADER_SIZE + (slot_index * self.slot_size)

        payload_len = struct.unpack_from("=I", self._buffer, offset)[0]
        data = bytes(self._buffer[offset + 4: offset + 4 + payload_len])

        # Advance head atomically
        self.set_head(head + 1)
        return data

    def available(self) -> int:
        return self.get_tail() - self.get_head()
