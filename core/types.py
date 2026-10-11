"""
APEX_AURA Core Types and Data Models.
Provides strictly typed, zero-overhead structures for the cognitive fabric.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class DecisionTier(str, Enum):
    TIER_0_DETERMINISTIC_JEV = "tier_0_jev"
    TIER_1_EDGE_CLEF = "tier_1_clef"
    TIER_2_REFLEX_LAYA = "tier_2_laya"
    TIER_3_SOVEREIGN_NIM = "tier_3_nim"
    TIER_4_CONSTRAINT_ANYJEV = "tier_4_anyjev"


class ActionType(str, Enum):
    CLICK = "click"
    KEYSTROKE = "keystroke"
    API_CALL = "api_call"
    DB_MUTATION = "db_mutation"
    RADIO_BEAM_STEER = "radio_beam_steer"


@dataclass(frozen=True)
class IngressPacket:
    packet_id: str
    timestamp_ns: int
    source_slice: str
    intent: str
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionItem:
    action_type: ActionType
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    inverse_action: Optional[ActionItem] = None


@dataclass
class ActionContract:
    contract_id: str
    intent: str
    target_action: ActionItem
    pre_predicate: Callable[[Dict[str, Any]], bool]
    post_predicate: Callable[[Dict[str, Any]], bool]
    compensating_action: Optional[ActionItem] = None
    timeout_ms: float = 50.0

    def verify_pre(self, state: Dict[str, Any]) -> bool:
        return self.pre_predicate(state)

    def verify_post(self, state: Dict[str, Any]) -> bool:
        return self.post_predicate(state)


@dataclass
class DecisionVerdict:
    decision_id: str
    tier_selected: DecisionTier
    latency_ms: float
    contract: ActionContract
    audit_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditRecord:
    record_id: str
    timestamp_ns: int
    decision_id: str
    tier: str
    intent: str
    hash_digest: str
    signature: str
    status: str = "COMMITTED"
