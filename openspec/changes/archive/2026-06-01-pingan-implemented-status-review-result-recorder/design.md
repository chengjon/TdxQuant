## Context

The promotion readiness rollup now emits `implemented_status_review_packet`. That packet packages machine-derived readiness state for manual review, but the human review outcome is still out-of-band. Without a controlled review-result artifact, later status-transition work would have to rely on unstructured notes.

## Goals / Non-Goals

**Goals:**

- Add a task manager recorder that writes a deterministic `tdx.desktop_trade.pingan_implemented_status_review_result.v1` artifact.
- Support dry-run preview and overwrite protection.
- Allow `approve`, `reject`, and `defer` outcomes with explicit reviewer, reason, and timestamp.
- Fail closed when `approve` is requested for a blocked or ineligible review packet.
- Keep the recorder explicit about not modifying `FUNCTION_TREE.md` and not executing PingAn workflows.

**Non-Goals:**

- Do not promote D-07/D-08 to `[已实现]`.
- Do not implement automatic status transition or FUNCTION_TREE editing.
- Do not execute broker, desktop, trading, report, catalog, bundle, or task workflows from the packet.
- Do not add runtime catalog/preset discovery in this slice.

## Decisions

- Implement `TdxTaskManager.pingan_implemented_status_review_result(...)` as the public task API. This keeps the review result in the existing task surface alongside the rollup and live/manual acceptance recorder.
- Load either a direct packet artifact or a rollup artifact containing `implemented_status_review_packet`. This keeps the operator workflow flexible while retaining a single packet schema check.
- Use `review_result_record` metadata in the task result and place the full artifact under `implemented_status_review_result`.
- Require non-empty `reviewer`, `outcome`, `reason`, and source packet path. `reviewed_at` defaults to current UTC if not provided.
- Keep CLI support for direct task invocation, but skip catalog registration so this remains a D-07/D-08 evidence step rather than an E-11 discovery slice.

## Risks / Trade-offs

- The artifact creates a durable human-review signal, but it still does not prove production readiness or complete implementation. The artifact and return record must include `function_tree_status_transition_executed=false` and `automatic_status_transition_allowed=false`.
- `reject` and `defer` can be recorded against blocked packets because those outcomes are review notes, not status-promotion authorization. `approve` is stricter and requires the packet to be eligible.
