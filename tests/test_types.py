import unittest
import time
from core.types import IngressPacket, ActionItem, ActionType, ActionContract, DecisionTier


class TestCoreTypes(unittest.TestCase):
    def test_ingress_packet_creation(self):
        pkt = IngressPacket(
            packet_id="pkt_test_101",
            timestamp_ns=time.perf_counter_ns(),
            source_slice="6g_urllc_slice_0",
            intent="DISMISS_MODAL",
        )
        self.assertEqual(pkt.packet_id, "pkt_test_101")
        self.assertEqual(pkt.intent, "DISMISS_MODAL")

    def test_action_contract_verification(self):
        contract = ActionContract(
            contract_id="contract_001",
            intent="TEST_ACTION",
            target_action=ActionItem(ActionType.CLICK, "btn.ok"),
            pre_predicate=lambda s: s.get("ready", False),
            post_predicate=lambda s: s.get("done", False),
        )
        self.assertTrue(contract.verify_pre({"ready": True}))
        self.assertFalse(contract.verify_pre({"ready": False}))
        self.assertTrue(contract.verify_post({"done": True}))


if __name__ == "__main__":
    unittest.main()
