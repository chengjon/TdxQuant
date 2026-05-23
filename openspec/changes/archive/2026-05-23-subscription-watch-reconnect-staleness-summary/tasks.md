## 1. Spec

- [x] Add OpenSpec deltas for reconnect staleness summary and bridge HTTP forwarding.
- [x] Validate the OpenSpec change before implementation.

## 2. Tests

- [x] Add subscription summary tests for default, stale, fresh/not-applicable, and governance reconnect behavior.
- [x] Add bridge HTTP, bridge registry, and CLI parser/dispatch tests for `reconnect_stale_after_seconds`.

## 3. Implementation

- [x] Extend subscription-watch status summary and advisory governance with opt-in reconnect staleness.
- [x] Thread `reconnect_stale_after_seconds` through controller, bridge HTTP, bridge registry, and bridge CLI.

## 4. Registry And Verification

- [x] Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary.
- [x] Run focused tests, registry validation, OpenSpec validation, and whitespace checks.
- [x] Archive the OpenSpec change and rerun verification.
