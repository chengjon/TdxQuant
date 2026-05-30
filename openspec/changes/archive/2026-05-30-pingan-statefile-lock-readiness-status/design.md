## Context

PingAn `dialog_readiness` is a read-only lifecycle diagnostic. It already reports configured artifact target paths under `dialog_readiness.artifact_targets`, but the lifecycle payload does not explicitly say that no statefile lock or ownership token exists for this command.

## Goals / Non-Goals

**Goals:**

- Add `statefile_lock_status` to `desktop_lifecycle_gate_status`.
- Make lock/write non-ownership explicit and machine-readable.
- Include the resolved artifact target paths used by dialog readiness.
- Keep process/window lifecycle ownership in remaining gates until real ownership and locking exist.
- Preserve D-07/D-08 partial status semantics in `FUNCTION_TREE.md`.

**Non-Goals:**

- Do not acquire locks or owner tokens.
- Do not write last-order state, event logs, submission ledger entries, or trade audit artifacts.
- Do not supervise, start, stop, or restart the PingAn desktop process.
- Do not mark D-07 or D-08 `[已实现]`.

## Decisions

- Represent lock ownership as `desktop_lifecycle_gate_status.statefile_lock_status` rather than as a health check. This keeps dialog lookup pass/fail semantics unchanged.
- Use `status=not_acquired`, `execution_mode=readonly_lock_status`, `lock_acquired=false`, and false write flags to make the non-owning boundary explicit.
- Include `artifact_targets` in the status so consumers can see what would be relevant for future lifecycle ownership without implying those files were touched.

## Risks / Trade-offs

- [Risk] Consumers might treat known paths as ownership. -> The status reports `lock_acquired=false` and `owner_token=null`, and FUNCTION_TREE records that no write or lock ownership occurred.
- [Risk] Future lifecycle control may need actual lock semantics. -> This change reserves a stable status location while keeping the executable lock behavior out of scope.
