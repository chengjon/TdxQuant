# Tasks

## 1. Specification

- [x] 1.1 Add proposal, design, spec deltas, and tasks for explicit supervisor tick.
- [x] 1.2 Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] 2.1 Add failing controller tests for active backoff wait, expired backoff recovery, failed recovery backoff, and no-action tick.
- [x] 2.2 Add failing bridge HTTP and registry tests for supervisor tick dispatch.
- [x] 2.3 Add failing CLI parser/dispatch tests for `bridge watch-supervisor-tick`.

## 3. Implementation

- [x] 3.1 Persist recoverable `start_request` on restart-backoff state without expanding compact diagnostics.
- [x] 3.2 Implement `SubscriptionWatchBackgroundController.supervisor_tick()`.
- [x] 3.3 Add HTTP, registry, and CLI supervisor tick dispatch.
- [x] 3.4 Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] 4.1 Run focused tests.
- [x] 4.2 Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
