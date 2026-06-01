## Why

Managed daemon lifecycle code now shares PID liveness, ownership, provenance, and restart/backoff primitives, but file lock handling remains duplicated in the provider replay statefile writer and subscription watch control/supervisor paths. Shared lifecycle file lock primitives make statefile and control lock behavior auditable in one place without changing daemon execution semantics.

## What Changes

- Add managed lifecycle file lock primitives for non-blocking local lock acquisition and release.
- Reuse the primitive from provider replay lifecycle statefile writes and subscription watch control/supervisor lock paths while preserving current public behavior.
- Add focused tests for acquired, blocked, and released lock outcomes plus adapter-level regression coverage.
- Update `FUNCTION_TREE.md` evidence for B-16 to record shared file lock coverage and retain explicit lifecycle boundaries.

## Capabilities

### New Capabilities

### Modified Capabilities
- `tdx-managed-process-lifecycle`: Add shared advisory file lock primitives for local daemon lifecycle state/control files.

## Impact

- Affected code: `tdxquant/managed_lifecycle.py`, `tdxquant/provider_transport_replay.py`, `tdxquant/subscription_watch_background.py`.
- Affected tests: `tests/test_managed_lifecycle.py`, `tests/test_provider_transport_replay.py`, `tests/test_subscription_watch_background.py`.
- Affected registry/specs: `FUNCTION_TREE.md`, `openspec/specs/tdx-managed-process-lifecycle/spec.md` after archive.
- No new external dependency, no public daemon CLI/API contract change, and no PingAn trade lifecycle migration.
