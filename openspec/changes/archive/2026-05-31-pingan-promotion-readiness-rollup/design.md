## Context

Existing PingAn promotion evidence is intentionally split across several read-only or evidence-producing surfaces:

- `promotion_gate_status` from trade preflight covers provider/broker ownership and safety gates.
- `desktop_lifecycle_gate_status` from dialog readiness covers passive lifecycle/dialog lookup evidence.
- `acceptance_outcome_coverage_status` from trade audit daily/period reports covers automated outcome coverage and optional manual/live acceptance evidence.

Each surface is useful, but D-07/D-08 promotion work benefits from a single report that explains the aggregate gate state. This change adds that report without triggering any of the evidence-producing commands.

## Goals / Non-Goals

**Goals:**

- Read one or more existing JSON evidence files.
- Extract known evidence payloads from either the root object or common `data` wrappers.
- Produce `promotion_readiness_rollup` with gate statuses, completed gates, incomplete gates, missing evidence kinds, and explicit boundaries.
- Expose the rollup through `TdxTaskManager` and `task pingan-promotion-readiness-rollup`.
- Preserve D-07/D-08 `[部分实现]`.

**Non-Goals:**

- Do not run preflight, dialog readiness, trade execution, report generation, catalog workflows, or broker probes.
- Do not infer production readiness from missing or stale evidence.
- Do not promote D-07/D-08 to `[已实现]`.
- Do not design a full governance dashboard.

## Decisions

1. Use file-based evidence inputs.

   The rollup accepts paths to already-created JSON artifacts. This makes side effects explicit and prevents the task from becoming an orchestrator for PingAn workflows.

2. Keep gate logic transparent.

   The task maps input evidence to named gates:

   - `provider_broker_ownership`
   - `safety_gates`
   - `desktop_lifecycle`
   - `audit_evidence`
   - `live_manual_acceptance`
   - `acceptance_evidence`

   A gate is complete only when its source evidence explicitly reports a complete/ready state.

3. Use partial status until every gate is complete.

   `promotion_readiness_rollup.status` is `complete` only when every gate is complete. Otherwise it is `partial`. Even complete rollup output is still evidence for a later status-promotion change, not the promotion itself.

## Risks / Trade-offs

- Evidence files can be stale or hand-edited. The rollup records source paths and missing evidence, but it does not verify provenance.
- Some existing evidence surfaces use `partial` even when they contain useful sub-gate evidence. The rollup treats only explicit complete/ready fields as complete to avoid overclaiming.
- The rollup creates a clearer path to promotion, but the actual status transition still requires a separate, explicit FUNCTION_TREE change.
