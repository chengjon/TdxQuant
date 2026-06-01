## Context

The review-result recorder writes a controlled artifact for `approve`, `reject`, or `defer`. A later status transition should not consume that artifact blindly. It needs a narrow gate that checks the artifact is recorder-produced, approved, still points at D-07/D-08, and still carries the explicit non-transition boundary from the recorder.

## Goals / Non-Goals

**Goals:**

- Add `TdxTaskManager.pingan_implemented_status_transition_gate(...)`.
- Validate review result schema and recorder provenance.
- Require `outcome=approve`, `target_nodes=["D-07", "D-08"]`, `packet_review_status=ready_for_manual_review`, `packet_decision=eligible_for_review`, and `implemented_status_eligible=true`.
- Require prior artifacts to say `function_tree_status_transition_executed=false`, `automatic_status_transition_allowed=false`, `order_submitted=false`, and `control_dispatch_executed=false`.
- Return a checklist that a maintainer can use for a separate reviewed status-transition change.

**Non-Goals:**

- Do not promote D-07/D-08 to `[已实现]`.
- Do not edit `FUNCTION_TREE.md` automatically.
- Do not execute PingAn broker, desktop, trade, report, catalog, task, or bundle workflows.
- Do not regenerate readiness evidence or re-run the review-result recorder.

## Decisions

- The gate is read-only by default and writes no artifact in this slice. The result payload is enough to validate the state before a separate transition implementation.
- Use schema `tdx.desktop_trade.pingan_implemented_status_transition_gate.v1`.
- Keep the public task name aligned with the existing chain: `pingan_implemented_status_transition_gate` and CLI command `pingan-implemented-status-transition-gate`.
- Treat missing or invalid provenance as blocked rather than an invalid request. File load/schema failures remain invalid request; content that fails checks produces a blocked gate so maintainers can inspect every blocker at once.
- Register this in `FUNCTION_TREE.md` as D-07/D-08 partial evidence only. It is a pre-transition gate, not the transition.

## Risks / Trade-offs

- The gate can make the transition path look close to complete. To avoid overclaiming, the payload and FUNCTION_TREE boundary must repeatedly state `function_tree_status_transition_executed=false` and `manual_status_transition_required=true`.
- The gate trusts the review-result artifact fields rather than re-reading every source readiness artifact. That keeps the slice small; deeper freshness/commit verification belongs in a later transition implementation if needed.
