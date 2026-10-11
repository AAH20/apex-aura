# APEX_AURA Diagram Repository (Diagram-Design Standard)

This repository houses the formal, fully annotated architectural diagrams for **APEX_AURA**, ensuring zero orphaned arrows, fully typed communication channels, and clear subsystem boundaries.

---

## 1. State Machine: Multi-Tier Decision & Action Contract Lifecycle

```mermaid
stateDiagram-v2
    [*] --> INGRESS_SHM_POLL: Packet Arrived via BlueField-3 DPU
    
    state INGRESS_SHM_POLL {
        [*] --> AtomicSpinlockWait
        AtomicSpinlockWait --> ReadHeader: Slot Ready
        ReadHeader --> PayloadUnpack: TSSP Header Valid
    }

    PayloadUnpack --> POLICY_SECURITY_VERIFY: Payload Decoded

    state POLICY_SECURITY_VERIFY {
        [*] --> ClefWasmCheck
        ClefWasmCheck --> WatsonxPolicyEval: Token Budget Clean
        WatsonxPolicyEval --> PolicyApproved: Guardrails Intact
        WatsonxPolicyEval --> PolicyRejected: PII / Violation Detected
    }

    PolicyRejected --> QUARANTINE_LOG: Security Fault
    QUARANTINE_LOG --> [*]: Alert watsonx.governance

    PolicyApproved --> ROUTING_TRIAGE: Select Solver Engine

    state ROUTING_TRIAGE {
        [*] --> CheckDeterministicCache
        CheckDeterministicCache --> FastPathJev: Cache / Pattern Match (O(k))
        CheckDeterministicCache --> ReflexLaya: Ambiguous Pattern Detected
        CheckDeterministicCache --> DeepStrategicNIM: Multi-Step Planning Required
        CheckDeterministicCache --> ExactAnyJev: Constraint Optimization Required
    }

    FastPathJev --> CONTRACT_PRE_ASSERT: Action Selected (0.001ms)
    ReflexLaya --> CONTRACT_PRE_ASSERT: Action Selected (4.500ms)
    DeepStrategicNIM --> CONTRACT_PRE_ASSERT: Action Selected (14.200ms)
    ExactAnyJev --> CONTRACT_PRE_ASSERT: Action Selected (1.100ms)

    state CONTRACT_PRE_ASSERT {
        [*] --> ReadSystemInvariant
        ReadSystemInvariant --> CheckDOM_Or_AX: Accessibility Scan
        CheckDOM_Or_AX --> PushRollbackStack: Pre-Conditions Confirmed
        CheckDOM_Or_AX --> AbortAction: Pre-Conditions Invalid
    }

    AbortAction --> [*]: State Intact, Action Canceled
    PushRollbackStack --> DISPATCH_HARDWARE: Trigger Atomic Injection

    state DISPATCH_HARDWARE {
        [*] --> InjectDirectHID: uinput / CoreGraphics / gRPC
        InjectDirectHID --> AwaitSettlementDelta: 10ms Sweep
    }

    AwaitSettlementDelta --> CONTRACT_POST_ASSERT: Read Post-State

    state CONTRACT_POST_ASSERT {
        [*] --> VerifyPostCondition
        VerifyPostCondition --> CommitSuccess: Condition True
        VerifyPostCondition --> TriggerRollback: Condition False OR Timeout
    }

    CommitSuccess --> IMMUTABLE_AUDIT_LOG: Pop Rollback Stack
    IMMUTABLE_AUDIT_LOG --> [*]: Stream TSSP Frame

    TriggerRollback --> ROLLBACK_COMPENSATION: Pop LIFO Stack
    
    state ROLLBACK_COMPENSATION {
        [*] --> DispatchInverseAction
        DispatchInverseAction --> VerifyCleanBaseline
    }

    VerifyCleanBaseline --> [*]: Clean State Restored (0 Dirty State)
```

---

## 2. Silicon-to-Memory Data Pipeline: BlueField-3 DOCA & POSIX SHM

```mermaid
flowchart TD
    subgraph HARDWARE_DPU["NVIDIA BlueField-3 DPU (400 Gbps RoCEv2)"]
        PHY_PORT["Dual QSFP112 Optical Links"]
        DOCA_CORE["DOCA Flow Hardware Engine"]
        TLS_ACCEL["Hardware TLS 1.3 Offload Engine"]
        DMA_ENGINE["GPUDirect Storage & Host DMA Controller"]
        PHY_PORT --> DOCA_CORE
        DOCA_CORE --> TLS_ACCEL
        TLS_ACCEL --> DMA_ENGINE
    end

    subgraph POSIX_SHM["Zero-Copy POSIX /dev/shm Ring Buffer (LMAX Disruptor)"]
        HEADER["Disruptor Ring Header (64-byte Cache-Line Aligned)\n[Head: uint64 | Tail: uint64 | Mask: 0x3FFF | Flags: uint32]"]
        SLOT_0["Slot 0: 64 KB Packet Buffer (TSSP Binary Format)"]
        SLOT_1["Slot 1: 64 KB Packet Buffer (TSSP Binary Format)"]
        SLOT_N["Slot N: 64 KB Packet Buffer (TSSP Binary Format)"]
        DMA_ENGINE -->|PCIe Gen5 x16 DMA Write| SLOT_0
        DMA_ENGINE -->|PCIe Gen5 x16 DMA Write| SLOT_1
        DMA_ENGINE -->|PCIe Gen5 x16 DMA Write| SLOT_N
    end

    subgraph COGNITIVE_CONSUMER["APEX_AURA Cognitive Consumer"]
        ATOMIC_POLL["Nanosecond Atomic Pointer Poller (<2μs)"]
        DESER["Zero-Copy TSSP Ingress Parser"]
        ROUTER_IN["Multi-Tier Decision Router"]
        HEADER --> ATOMIC_POLL
        SLOT_0 -->|Memory Pointer Handoff| DESER
        DESER --> ROUTER_IN
    end
```

---

## 3. Class Diagram: Core Domain & Sovereign Contracts

```mermaid
classDiagram
    class IngressPacket {
        +string packet_id
        +float timestamp_ns
        +string source_slice
        +bytes raw_payload
        +to_tssp_frame() TSSPFrame
    }

    class ActionContract {
        +string contract_id
        +string intent
        +Callable pre_predicate
        +Callable post_predicate
        +Action target_action
        +Action compensating_action
        +float timeout_ms
        +verify_pre(state) bool
        +verify_post(state) bool
    }

    class RollbackJournal {
        -List~Action~ _lifo_stack
        +push(compensating_action) void
        +pop() Action
        +execute_rollback(executor) bool
        +depth() int
    }

    class DecisionVerdict {
        +string decision_id
        +string tier_selected
        +float latency_ms
        +ActionContract contract
        +dict audit_metadata
    }

    class WatsonxAuditRecord {
        +string record_id
        +string blake3_hash
        +string ed25519_signature
        +dict compliance_context
        +commit_to_vault() bool
    }

    IngressPacket --> DecisionVerdict : Evaluated by Router
    DecisionVerdict --> ActionContract : Generates
    ActionContract --> RollbackJournal : Pushes inverse
    DecisionVerdict --> WatsonxAuditRecord : Attested by
```

---

## 4. Deployment Topology: Red Hat OpenShift AI & DGX Cloud

```mermaid
graph TB
    subgraph CLOUD_HYBRID["Sovereign Red Hat OpenShift AI Fabric"]
        subgraph INFRA_NODES["Bare-Metal DGX Nodes (H100 / B200)"]
            POD_NIM["NVIDIA NIM Pod\n(TensorRT-LLM / Triton)"]
            POD_GRANITE["IBM Granite 3.0 Pod\n(Open Sovereign LLM)"]
            POD_DPU["DOCA Ingress DaemonSet\n(BlueField-3 Host Driver)"]
        end

        subgraph CONTROL_PLANE["Control Plane & Governance"]
            WX_GOV_SVC["watsonx.governance Pod\n(Audit Vault & Risk Monitor)"]
            WX_DATA_SVC["watsonx.data Lakehouse\n(Apache Iceberg / Presto)"]
            AURA_HYPERVISOR["APEX_AURA Hypervisor Pod\n(Cognitive Router & Action Kernel)"]
        end
    end

    POD_DPU -->|IPC /dev/shm| AURA_HYPERVISOR
    AURA_HYPERVISOR <-->|gRPC sub-1ms| POD_NIM
    AURA_HYPERVISOR <-->|gRPC sub-1ms| POD_GRANITE
    AURA_HYPERVISOR -->|TLS 1.3 Mutual Auth| WX_GOV_SVC
    AURA_HYPERVISOR -->|Arrow Flight SQL| WX_DATA_SVC
```
