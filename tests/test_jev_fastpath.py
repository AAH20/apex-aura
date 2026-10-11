import unittest
from routing.jev_engine import JevEngine
from routing.clef_edge_router import ClefEdgeRouter


class TestRoutingFastPaths(unittest.TestCase):
    def test_jev_fastpath_hit(self):
        engine = JevEngine()
        res = engine.evaluate("DISMISS_MODAL")
        self.assertIsNotNone(res)
        action, lat = res
        self.assertEqual(action.target, "button.close")
        self.assertLess(lat, 0.05)  # Under 50μs

    def test_clef_security_policy(self):
        clef = ClefEdgeRouter()
        ok, msg, lat = clef.evaluate_policy("SAFE_AGENT_DIRECTIVE")
        self.assertTrue(ok)

        blocked, msg, lat = clef.evaluate_policy("DROP TABLE users;")
        self.assertFalse(blocked)
        self.assertIn("VIOLATION", msg)


if __name__ == "__main__":
    unittest.main()
