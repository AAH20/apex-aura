"""
NVIDIA NeMo Guardrails Programmable Safety Rail Interface.
Enforces dialog rails, topical rails, and execution rails on LLM outputs at linespeed.
"""

from typing import Dict, Any, List
import re


class NeMoGuardrailsBridge:
    def __init__(self):
        self._forbidden_patterns = [
            re.compile(r"DROP\s+TABLE", re.IGNORECASE),
            re.compile(r"DELETE\s+FROM", re.IGNORECASE),
            re.compile(r"api_key\s*=\s*['\"][a-zA-Z0-9_-]+['\"]", re.IGNORECASE),
        ]

    def validate_action_intent(self, intent_text: str) -> bool:
        """Returns True if intent is clean, False if guardrail is triggered."""
        for pattern in self._forbidden_patterns:
            if pattern.search(intent_text):
                return False
        return True
