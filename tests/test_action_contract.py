import unittest
from core.types import ActionContract, ActionItem, ActionType
from execution.action_contract import ActionContractEngine
from execution.rollback_journal import RollbackJournal


class TestContractAndRollback(unittest.TestCase):
    def test_successful_contract_execution(self):
        journal = RollbackJournal()
        engine = ActionContractEngine(journal)

        contract = ActionContract(
            contract_id="c_success",
            intent="UPDATE_CONFIG",
            target_action=ActionItem(ActionType.API_CALL, "api.config", {"val": 1}),
            pre_predicate=lambda s: s.get("status") == "IDLE",
            post_predicate=lambda s: s.get("status") == "UPDATED",
            compensating_action=ActionItem(ActionType.API_CALL, "api.config", {"val": 0}),
        )

        success, code, state = engine.execute(
            contract,
            {"status": "IDLE"},
            lambda act: {"status": "UPDATED"},
        )
        self.assertTrue(success)
        self.assertEqual(code, "COMMITTED")
        self.assertEqual(journal.depth(), 0)

    def test_post_condition_failure_triggers_rollback(self):
        journal = RollbackJournal()
        engine = ActionContractEngine(journal)

        contract = ActionContract(
            contract_id="c_fail",
            intent="FAULTY_MUTATION",
            target_action=ActionItem(ActionType.DB_MUTATION, "db.orders", {}),
            pre_predicate=lambda s: True,
            post_predicate=lambda s: False,  # Will fail
            compensating_action=ActionItem(ActionType.DB_MUTATION, "db.orders.undo", {}),
        )

        success, code, state = engine.execute(
            contract,
            {"state": "ORIGINAL"},
            lambda act: {"state": "DIRTY"},
        )
        self.assertFalse(success)
        self.assertIn("ROLLED_BACK", code)
        self.assertEqual(journal.depth(), 0)  # Unwound


if __name__ == "__main__":
    unittest.main()
