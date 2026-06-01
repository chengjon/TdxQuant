## Why

Provider replay, subscription watch background control, and PingAn trading lifecycle code all implement the same lifecycle roles independently: process liveness, owner PID/statefile diagnostics, lock ownership, supervisor decisions, and restart/backoff projections. The architecture review in `docs/reviews/2026-06-01-architecture-deepening-opportunities.md` identifies this as the highest-leverage real seam because at least three adapters already exist.

This change starts that consolidation without reopening high-risk desktop trading behavior. It introduces a shared managed-process lifecycle module and wires it into the lower-risk provider replay and subscription watch background lines first.

## What Changes

- Add a new `tdxquant.managed_lifecycle` module for deterministic lifecycle primitives:
  - PID coercion and liveness probes.
  - Process ownership diagnostics.
  - Shared lifecycle provenance metadata for adapters.
  - Restart/backoff projection helpers.
- Wire provider transport replay daemon status/ownership diagnostics through the shared primitives.
- Wire subscription watch background PID parsing/liveness and statefile ownership projection through the shared primitives.
- Preserve existing public CLI/manager behavior and output compatibility, only adding explicit shared-lifecycle provenance fields.
- Update `FUNCTION_TREE.md` evidence for the relevant implemented lifecycle node without changing its status.

## Capabilities

### New Capabilities

- `tdx-managed-process-lifecycle`: Shared local managed-process lifecycle primitives for statefile ownership, PID liveness, process ownership diagnostics, and restart/backoff projections.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: Provider replay lifecycle diagnostics SHALL report that they are backed by the shared managed-process lifecycle primitives.
- `tdx-task-subscription-watch-background-control`: Subscription watch background ownership diagnostics SHALL report that they are backed by the shared managed-process lifecycle primitives.
- `tdx-function-tree-registry`: `FUNCTION_TREE.md` SHALL cite the shared lifecycle module and this OpenSpec change as evidence for lifecycle governance hardening.

## Impact

- Code:
  - Add `tdxquant/managed_lifecycle.py`.
  - Update `tdxquant/provider_transport_replay.py`.
  - Update `tdxquant/subscription_watch_background.py`.
  - Add focused tests for shared primitives and both adapters.
- Docs/specs:
  - Add OpenSpec capability `tdx-managed-process-lifecycle`.
  - Update provider replay, subscription watch background, and function-tree specs.
  - Update `FUNCTION_TREE.md` evidence/boundary text.
- Non-goals:
  - No CLI syntax changes.
  - No socket/server startup behavior changes.
  - No real broker, desktop automation, or PingAn trade lifecycle refactor in this slice.
  - No attempt to replace every existing lifecycle helper at once.
