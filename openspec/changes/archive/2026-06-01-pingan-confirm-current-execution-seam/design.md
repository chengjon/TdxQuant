## Context

`confirm_current` differs from buy/sell order execution:

- It confirms an already visible broker dialog rather than submitting a new order.
- It has no `code`, `price`, `quantity`, `submission_key`, or submission-ledger participation.
- It returns non-finalized metadata for pre-dispatch gate failures and lookup/click failures, but finalizes artifact writes when the confirmation is advanced.

The existing order seam should remain order-specific. This change adds a small confirm-current seam that keeps the confirm semantics separate while applying the same policy boundary.

## Goals

- Introduce `PingAnConfirmCurrentExecutionRequest` with method identity, timing label, profile options, broker, and a nullable request context.
- Introduce `execute_pingan_confirm_current(...)` that:
  - returns the existing gate-rejection result without running UI dispatch when the boundary risk gate fails,
  - captures timing around the UI dispatch callback only after gates pass,
  - attaches manager/safety metadata for non-advanced confirmation results,
  - calls the existing manager finalize function when confirmation is advanced.
- Keep all dialog lookup/click/result-close logic in the manager dispatch callback for this slice.

## Non-Goals

- Do not refactor dialog lookup internals or desktop primitives.
- Do not create generic workflow execution infrastructure.
- Do not modify public `confirm_current` parameters, CLI/task/catalog entries, or runtime artifacts beyond the existing behavior.

## Compatibility

The public method signature stays unchanged. Pre-dispatch rejection, failed lookup/click, warning, and success results keep their current result shape and metadata. Successful confirmation continues to write the same finalized trade artifacts through `_finalize_result`; non-advanced outcomes remain metadata-attached but not finalized into live trade artifacts.

## Validation

Validation focuses on the manager boundary:

- A new focused test patches `execute_pingan_confirm_current` and UI lookup, calls `manager.pingan.confirm_current(...)`, and asserts normalized request identity plus no pre-seam UI lookup.
- Existing confirm-current tests continue to cover owner-lock/broker-readiness rejections, lookup/click paths, result dialog warnings, metadata, and artifact behavior.

