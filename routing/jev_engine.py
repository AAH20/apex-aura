"""
APEX_AURA Tier 0 Deterministic Jev Rule Engine.
Sub-microsecond (<0.002ms) rule table lookup without neural network invocation.
"""

from typing import Dict, Optional, Tuple
import time
from core.types import ActionItem, ActionType


class JevEngine:
    def __init__(self):
        self._rules: Dict[str, ActionItem] = {
            "DISMISS_MODAL": ActionItem(
                action_type=ActionType.CLICK,
                target="button.close",
                parameters={"x": 0.85, "y": 0.15},
                inverse_action=ActionItem(ActionType.KEYSTROKE, "keyboard", {"keys": ["Escape"]}),
            ),
            "CONFIRM_TRANSACTION": ActionItem(
                action_type=ActionType.CLICK,
                target="button.submit",
                parameters={"x": 0.50, "y": 0.80},
                inverse_action=ActionItem(ActionType.API_CALL, "api.orders.undo", {}),
            ),
        }

    def evaluate(self, intent: str) -> Optional[Tuple[ActionItem, float]]:
        start_ns = time.perf_counter_ns()
        normalized_intent = intent.strip().upper()
        if normalized_intent in self._rules:
            action = self._rules[normalized_intent]
            elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
            return action, elapsed_ms
        return None
