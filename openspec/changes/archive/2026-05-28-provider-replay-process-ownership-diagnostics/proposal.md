# Provider Replay Process Ownership Diagnostics

## Why

E-06 now has statefile ownership, one-shot daemon control, a foreground supervisor, and opt-in restart/backoff. The remaining safety gap is an explicit ownership diagnostic that distinguishes a valid statefile from a live, tool-owned process identity. Without that summary, callers must infer ownership from scattered fields.

## What Changes

- Add a read-only process ownership diagnostic helper.
- Combine statefile validity, provider id match, config hash match, owner token presence/match, PID liveness, and optional process identity match.
- Include the ownership diagnostic in `provider-replay daemon status`.
- Let `provider-replay lifecycle-readiness --include-statefile-check` count owned process identity when diagnostics prove it.
- Add focused tests for owned, foreign, and mismatched process identities.
- Update `FUNCTION_TREE.md` E-06 evidence and boundary.

## Non-Goals

- No default process command-line inspection.
- No process killing behavior changes.
- No port ownership inference.
- No real provider adapter.
- No broker/workflow/write readiness claim.
- No E-06 status promotion to `[已实现]`.

