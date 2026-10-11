"""
APEX_AURA Tier 2 Host Laya Client.
Connects to the active local Laya model on port 8765 (convaiinnovations/laya-typed-decisions).
"""

import json
import time
import urllib.request
from typing import Dict, Any, Optional


class LayaClient:
    def __init__(self, endpoint: str = "http://127.0.0.1:8765/v1/systemone"):
        self.endpoint = endpoint

    def query_decision(self, context: str) -> Optional[Dict[str, Any]]:
        start_ns = time.perf_counter_ns()
        try:
            payload = json.dumps({
                "context": context,
                "criteria": ["safety", "latency", "reversibility"],
            }).encode("utf-8")
            req = urllib.request.Request(
                self.endpoint,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=0.2) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                res["latency_ms"] = (time.perf_counter_ns() - start_ns) / 1_000_000.0
                return res
        except Exception:
            return None
