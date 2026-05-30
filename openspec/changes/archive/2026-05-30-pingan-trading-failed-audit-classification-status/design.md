## Context

The finalized PingAn audit path already writes a normalized `trade_audit` summary and `trade_audit_gate_status` for each finalized result. The status resolver now distinguishes replayed, rejected, confirmed, explicit exception, and generic failed outcomes. The gate status, however, only exposes the final covered status and not the classification signal.

## Goals / Non-Goals

**Goals:**

- Add a stable `audit_status_classification` object to `trade_audit_gate_status`.
- Make generic failed outcomes explicit with `source=generic_execution_failure`.
- Preserve existing status classification and artifact persistence behavior.
- Preserve D-07/D-08 partial status semantics in `FUNCTION_TREE.md`.

**Non-Goals:**

- Do not change `trade_audit.status` values.
- Do not alter order submission, dialog handling, or artifact write order.
- Do not implement exception popup handling, retry policy, live/manual acceptance, or production readiness.
- Do not mark D-07 or D-08 `[已实现]`.

## Decisions

- Build classification details in the gate-status builder from the finalized result data already present after audit metadata attachment.
- Treat `failed` as `generic_execution_failure` only when no explicit exception metadata is present. Explicit `desktop_exception` / `trade_exception` remains `exception`, not `failed`.
- Include boolean signals for idempotency skip, rejection, explicit exception metadata, and result success so readers can tell which branch classified the result.

## Risks / Trade-offs

- [Risk] Classification fields could be mistaken for runtime recovery. -> Boundary text states the signal is audit-only and does not implement retry, recovery, or acceptance.
- [Risk] Additional fields could disrupt strict consumers. -> Add fields without removing or renaming existing `trade_audit_gate_status` keys.
- [Risk] The classification logic could diverge from the resolver. -> Derive it from the same finalized result metadata and keep tests on public PingAn manager paths.

