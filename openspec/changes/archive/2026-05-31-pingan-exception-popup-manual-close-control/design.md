## Context

`trade dialog-readiness` already performs passive result dialog lookup, extracts dialog text, and classifies exception-like popup content with `exception_popup_lookup`. Its lifecycle status intentionally reports `exception_popup_handling_status.handling_available=false` because no stable close control exists.

`confirm_current` already has a bounded result-dialog close path after advancing a confirmation dialog, but that path is coupled to a trade workflow and writes trade artifacts through finalization. The new control needs to reuse the same lookup/click helpers while staying outside order submission and audit finalization.

## Goals / Non-Goals

**Goals:**

- Provide an explicit PingAn manager method for exception popup inspect/close.
- Expose the same control as stable `trade exception-popup`.
- Require an explicit `--confirm-close` acknowledgement before any popup close click.
- Only close a recognized exception-like result popup with a detected confirm button.
- Register the evidence in D-07/D-08 without changing their `[部分实现]` status.

**Non-Goals:**

- No automatic exception recovery, order retry, or resubmission.
- No task/catalog workflow entry and no workflow builder readiness claim.
- No broker readiness, live/manual acceptance, process ownership, supervisor, restart/backoff, or lifecycle statefile ownership changes.
- No trade audit/state/ledger writes for the popup control.

## Decisions

- Reuse `_find_result_dialog_for_lookup`, `_find_result_confirm_target_for_lookup`, `_extract_dialog_text_payload_from_sources`, `_build_pingan_exception_popup_lookup_detail`, and `_click_lookup_target`.
  - Rationale: these helpers already define the supported PingAn dialog lookup and click boundary.
  - Alternative considered: introduce a separate UIA selector. Rejected because it would create a second desktop-control path with different evidence semantics.

- Require both `action=close` and `confirm_close=true` before clicking.
  - Rationale: closing a live desktop popup is a side effect and must be explicitly operator-acknowledged.
  - Alternative considered: close whenever `--action close` is present. Rejected because accidental CLI invocation would have a live desktop side effect.

- Only close when exception-like popup text is recognized.
  - Rationale: ordinary order result dialogs are already handled by `confirm_current`; this control is scoped to exception popup handling.
  - Alternative considered: close any result dialog. Rejected because it would blur exception handling with normal result dialog management.

- Attach trade metadata and safety metadata, but do not finalize the result.
  - Rationale: this is a desktop dialog control, not a trade submission outcome. Finalization would write trade audit/state artifacts and overstate evidence.

## Risks / Trade-offs

- [Risk] A recognized exception popup may contain text not covered by the current keywords and therefore will not close. -> Mitigation: return inspect details and keep manual action required.
- [Risk] Operators may confuse close control with recovery. -> Mitigation: response payload, specs, and FUNCTION_TREE boundaries explicitly report `retry_executed=false`, `recovery_executed=false`, and `resubmission_executed=false`.
- [Risk] UI automation click can fail even after lookup succeeds. -> Mitigation: return click result details and do not claim popup closure unless the click result is OK.
