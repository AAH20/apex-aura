"""
APEX_AURA Action Contract Verification Engine.
Enforces mathematical pre/post invariants before physical/logical mutations.
"""

from __future__ import annotations
import time
from typing import Any, Callable, Dict, Tuple
from core.types import ActionContract, ActionItem
from execution.rollback_journal import RollbackJournal


class ActionContractEngine:
    """
    Executes and validates action contracts with microsecond atomic assertions.
    """

    def __init__(self, journal: RollbackJournal):
        self.journal = journal

    def execute(
        self,
        contract: ActionContract,
        current_state: Dict[str, Any],
        mutator: Callable[[ActionItem], Dict[str, Any]],
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Executes an action contract:
        1. Assert Pre-Condition -> if False, abort without mutation.
        2. Push compensating action to Rollback Journal.
        3. Dispatch mutation.
        4. Assert Post-Condition -> if False, trigger rollback.
        """
        # Step 1: Pre-condition check
        if not contract.verify_pre(current_state):
            return False, "PRE_CONDITION_VIOLATION", current_state

        # Step 2: Push compensation intent
        if contract.compensating_action:
            self.journal.push(contract.compensating_action)

        # Step 3: Execute physical/API mutation
        mutated_state = mutator(contract.target_action)

        # Step 4: Post-condition check
        if not contract.verify_post(mutated_state):
            # Rollback
            unwound = self.journal.execute_rollback()
            return False, f"POST_CONDITION_VIOLATION_ROLLED_BACK_{unwound}", current_state

        # Success - clean up journal entry
        self.journal.clear()
        return True, "COMMITTED", mutated_state
