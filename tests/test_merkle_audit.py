import unittest
import time
from core.types import IngressPacket
from governance.merkle_audit_ledger import MerkleAuditLedger
from routing.decision_router import MultiTierDecisionRouter


class TestMerkleAudit(unittest.TestCase):
    def test_audit_hash_chaining(self):
        ledger = MerkleAuditLedger()
        router = MultiTierDecisionRouter()

        pkt1 = IngressPacket("p1", time.perf_counter_ns(), "slice0", "DISMISS_MODAL")
        v1 = router.route_intent(pkt1)
        r1 = ledger.record_decision(v1)
        root1 = ledger.get_root_hash()

        pkt2 = IngressPacket("p2", time.perf_counter_ns(), "slice0", "DISMISS_MODAL")
        v2 = router.route_intent(pkt2)
        r2 = ledger.record_decision(v2)
        root2 = ledger.get_root_hash()

        self.assertNotEqual(root1, root2)
        self.assertEqual(ledger.total_records(), 2)


if __name__ == "__main__":
    unittest.main()
