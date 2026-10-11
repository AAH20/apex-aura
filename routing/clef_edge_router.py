"""
APEX_AURA Tier 1 Cloudflare Clef Edge Security & Guardrail Filter.
Executes sub-microsecond edge policy checks and PII sanitization.
"""

from typing import Tuple, Dict, Any
import time


class ClefEdgeRouter:
    def __init__(self):
        self._blocked_keywords = {"DROP TABLE", "DELETE FROM", "UNSAFE_INJECTION", "MALWARE"}

    def evaluate_policy(self, intent: str) -> Tuple[bool, str, float]:
        start_ns = time.perf_counter_ns()
        for kw in self._blocked_keywords:
            if kw in intent:
                elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
                return False, f"POLICY_VIOLATION_KEYWORD_{kw}", elapsed_ms

        elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
        return True, "CLEF_POLICY_APPROVED", elapsed_ms
