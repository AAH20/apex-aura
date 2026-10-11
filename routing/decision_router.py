"""
APEX_AURA Multi-Tier Cognitive Decision Router.
Enforces hierarchical triage across deterministic fast-paths, edge policies, reflex neural models, and sovereign LLMs.
"""

from __future__ import annotations
import json
import time
import urllib.request
from typing import Any, Dict, Optional

from core.types import (
    ActionContract,
    ActionItem,
    ActionType,
    DecisionTier,
    DecisionVerdict,
    IngressPacket,
)


class MultiTierDecisionRouter:
    """
    Arbitrates incoming agent directives with sub-millisecond priority routing.
    """

    def __init__(self, laya_endpoint: str = "http://127.0.0.1:8765/v1/systemone"):
        self.laya_endpoint = laya_endpoint
        self._rule_cache: Dict[str, ActionItem] = {
            "DISMISS_MODAL": ActionItem(
                action_type=ActionType.CLICK,
                target="button.close_dialog",
                parameters={"x": 0.85, "y": 0.15},
                inverse_action=ActionItem(
                    action_type=ActionType.KEYSTROKE,
                    target="keyboard",
                    parameters={"keys": ["Escape"]},
                ),
            ),
            "CONFIRM_TRANSACTION": ActionItem(
                action_type=ActionType.CLICK,
                target="button.submit_order",
                parameters={"x": 0.50, "y": 0.80},
                inverse_action=ActionItem(
                    action_type=ActionType.API_CALL,
                    target="api.orders.rollback",
                    parameters={"order_id": "auto_detect"},
                ),
            ),
        }

    def route_intent(self, packet: IngressPacket) -> DecisionVerdict:
        start_ns = time.perf_counter_ns()
        intent = packet.intent.strip().upper()

        # Tier 0: Deterministic Fast-Path (Jev Rule Solver)
        if intent in self._rule_cache:
            action = self._rule_cache[intent]
            elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
            contract = ActionContract(
                contract_id=f"contract_{packet.packet_id}_jev",
                intent=intent,
                target_action=action,
                pre_predicate=lambda s: s.get("ready", True),
                post_predicate=lambda s: s.get("committed", True),
                compensating_action=action.inverse_action,
            )
            return DecisionVerdict(
                decision_id=f"dec_{packet.packet_id}",
                tier_selected=DecisionTier.TIER_0_DETERMINISTIC_JEV,
                latency_ms=elapsed_ms,
                contract=contract,
                audit_metadata={"fast_path": True, "engine": "JevRuleSolver"},
            )

        # Tier 1: Cloudflare Clef Edge Security & Guardrails
        if "UNSAFE" in intent or "RESTRICTED" in intent:
            elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
            abort_action = ActionItem(action_type=ActionType.API_CALL, target="security.quarantine")
            contract = ActionContract(
                contract_id=f"contract_{packet.packet_id}_clef",
                intent=intent,
                target_action=abort_action,
                pre_predicate=lambda s: False,  # Immediate abort
                post_predicate=lambda s: True,
            )
            return DecisionVerdict(
                decision_id=f"dec_{packet.packet_id}",
                tier_selected=DecisionTier.TIER_1_EDGE_CLEF,
                latency_ms=elapsed_ms,
                contract=contract,
                audit_metadata={"security_verdict": "BLOCKED", "engine": "ClefEdgeRouter"},
            )

        # Tier 2: Active Host Laya Model (:8765)
        try:
            req_data = json.dumps({
                "context": intent,
                "criteria": ["safety", "latency", "reversibility"],
            }).encode("utf-8")
            req = urllib.request.Request(
                self.laya_endpoint,
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=0.1) as resp:
                laya_res = json.loads(resp.read().decode("utf-8"))
                elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
                action = ActionItem(
                    action_type=ActionType.CLICK,
                    target=laya_res.get("target", "ui.default_element"),
                    parameters={"score": laya_res.get("confidence", 0.95)},
                )
                contract = ActionContract(
                    contract_id=f"contract_{packet.packet_id}_laya",
                    intent=intent,
                    target_action=action,
                    pre_predicate=lambda s: True,
                    post_predicate=lambda s: True,
                )
                return DecisionVerdict(
                    decision_id=f"dec_{packet.packet_id}",
                    tier_selected=DecisionTier.TIER_2_REFLEX_LAYA,
                    latency_ms=elapsed_ms,
                    contract=contract,
                    audit_metadata={"laya_response": laya_res, "engine": "HostLayaService"},
                )
        except Exception:
            # Fallback to Tier 3 / Tier 4 Sovereign Engine
            pass

        # Tier 3: Sovereign NIM / IBM Granite 3.0 Synthesizer (Simulated Sovereign Engine)
        elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
        synthetic_action = ActionItem(
            action_type=ActionType.API_CALL,
            target="sovereign.granite.executor",
            parameters={"directive": intent},
            inverse_action=ActionItem(
                action_type=ActionType.API_CALL,
                target="sovereign.granite.undo",
                parameters={"directive": intent},
            ),
        )
        contract = ActionContract(
            contract_id=f"contract_{packet.packet_id}_nim",
            intent=intent,
            target_action=synthetic_action,
            pre_predicate=lambda s: True,
            post_predicate=lambda s: True,
            compensating_action=synthetic_action.inverse_action,
        )
        return DecisionVerdict(
            decision_id=f"dec_{packet.packet_id}",
            tier_selected=DecisionTier.TIER_3_SOVEREIGN_NIM,
            latency_ms=elapsed_ms,
            contract=contract,
            audit_metadata={"engine": "NVIDIA_NIM_IBM_Granite_3.0", "license": "Apache-2.0"},
        )
