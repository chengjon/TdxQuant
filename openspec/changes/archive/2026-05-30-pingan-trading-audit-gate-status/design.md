## Context

The standard PingAn trade finalization path already attaches `trade_audit`, writes last-order state, appends an order-event row, optionally appends a submission-ledger row, and writes one immutable audit artifact. These artifacts are strong evidence that a specific finalized result was persisted, but the evidence is spread across fields and file paths.

## Goals / Non-Goals

**Goals:**

- Expose a normalized `trade_audit_gate_status` object on finalized PingAn trade results.
- Keep the object derived from existing artifacts, without changing execution flow or persistence behavior.
- Preserve partial promotion semantics: this gate does not prove exception popup handling or acceptance coverage by itself.

**Non-Goals:**

- Do not change audit file schemas or report aggregation behavior.
- Do not create new audit artifacts beyond the existing finalized result artifact.
- Do not mark D-07/D-08 `[已实现]`.

## Decisions

- Build the gate status at the end of `_finalize_result`, after artifact paths are known. This lets the status cite the actual persisted paths without changing write order.
- Include both `covered_audit_status` and `remaining_audit_gate_statuses`. A confirmed result should not imply rejected/failed/exception coverage, and a rejected result should not imply success coverage.
- Treat submission ledger as optional, because only calls with a `submission_key` and request context write ledger rows.

## Risks / Trade-offs

- [Risk] Additional status could be mistaken for full audit acceptance. -> Include `status=partial`, current-only coverage, and remaining status names.
- [Risk] Existing tests might assume exact data shape. -> Add fields without removing or renaming existing `trade_audit` or `artifacts` keys.
- [Risk] Exception evidence is not currently a distinct audit status. -> Keep `exception` in remaining gate names and do not claim coverage.
