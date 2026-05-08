## 1. CLI Replay Policy

- [x] 1.1 Add an explicit nested `api` replay support matrix and reject unsupported replay commands before live manager construction.
- [x] 1.2 Harden flat replay command dispatch so unsupported flat commands return stable replay failure JSON instead of live bridge execution.
- [x] 1.3 Normalize replay selector handling for `--provider-mode`, `--fixture`, `--fixture-path`, and `--output` on supported CLI entrypoints.

## 2. Subscription Watch Replay Contract

- [x] 2.1 Return stable replay-mode completed task results with canonical artifact paths and legacy alias fields for `subscription-watch`.
- [x] 2.2 Normalize malformed or incomplete `subscription-watch` replay sources into stable `INVALID_REQUEST` failures without opening a live runtime session.

## 3. Verification And Documentation

- [x] 3.1 Add replay transport tests covering supported command matrix, selector behavior, `stdout`/`--output` mirroring, and no-live-fallback semantics.
- [x] 3.2 Update replay fixture and `subscription-watch` contract documentation to describe the stabilized CLI subprocess replay contract.
- [x] 3.3 Run targeted replay contract regression tests and confirm they pass before archiving the change.
