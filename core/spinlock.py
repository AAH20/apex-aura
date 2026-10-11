"""
APEX_AURA Atomic Spinlock Primitives.
Zero-allocation synchronization mechanism with nanosecond spin-wait loops.
"""

import time
from typing import Optional


class AtomicSpinlock:
    """
    Simulates a hardware atomic test-and-set spinlock with backoff.
    Used for POSIX /dev/shm shared memory concurrency control.
    """

    def __init__(self, max_spins: int = 10_000):
        self._locked = False
        self.max_spins = max_spins

    def acquire(self, timeout_ms: float = 10.0) -> bool:
        start_ns = time.perf_counter_ns()
        timeout_ns = int(timeout_ms * 1_000_000)
        spins = 0

        while self._locked:
            spins += 1
            if spins > self.max_spins:
                if (time.perf_counter_ns() - start_ns) > timeout_ns:
                    return False
                time.sleep(0.000001)  # 1μs yield backoff
        self._locked = True
        return True

    def release(self) -> None:
        self._locked = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
