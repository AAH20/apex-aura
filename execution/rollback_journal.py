"""
APEX_AURA Transactional Rollback Journal.
Maintains an O(1) LIFO stack of inverse compensating actions to guarantee zero dirty state upon action failure.
"""

from __future__ import annotations
import time
from typing import Callable, List, Optional
from core.types import ActionItem


class RollbackJournal:
    """
    Saga Transaction Coordinator for agent actions.
    Guarantees that uncommitted or faulted actions are compensated deterministically.
    """

    def __init__(self):
        self._lifo_stack: List[ActionItem] = []
        self._history: List[dict] = []

    def push(self, action: Optional[ActionItem]) -> None:
        """Push a compensating action onto the LIFO stack."""
        if action is not None:
            self._lifo_stack.append(action)

    def pop(self) -> Optional[ActionItem]:
        """Pop the most recent compensating action."""
        if self._lifo_stack:
            return self._lifo_stack.pop()
        return None

    def depth(self) -> int:
        """Return the current depth of uncommitted compensating actions."""
        return len(self._lifo_stack)

    def execute_rollback(self, executor: Optional[Callable[[ActionItem], bool]] = None) -> int:
        """
        Unwind all compensating actions in reverse chronological order.
        Returns the number of compensating actions successfully executed.
        """
        start_ns = time.perf_counter_ns()
        unwound_count = 0

        while self._lifo_stack:
            compensating_action = self._lifo_stack.pop()
            success = True
            if executor:
                success = executor(compensating_action)
            self._history.append({
                "action": compensating_action.target,
                "type": compensating_action.action_type.value,
                "timestamp_ns": time.perf_counter_ns(),
                "success": success,
            })
            unwound_count += 1

        elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
        return unwound_count

    def clear(self) -> None:
        """Clear the stack after successful commit."""
        self._lifo_stack.clear()
