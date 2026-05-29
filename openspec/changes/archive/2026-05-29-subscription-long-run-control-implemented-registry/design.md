# Design

## Scope

This change is a registry closeout for existing subscription watch long-run control evidence. It does not introduce new lifecycle behavior. The codebase already exposes the relevant control surface through `SubscriptionWatchBackgroundController`, bridge HTTP routes, registry helpers, CLI commands, tests, and archived OpenSpec changes.

## Registry Model

B-16 covers the reconnect/backoff and long-running governance layer. E-09 covers the thicker subscription watch long-run wrapper. Their rows should become `[已实现]` only within the explicit operator-managed scope already implemented:

- persisted start request evidence for restartability
- explicit restart and restart preflight
- bounded restart backoff after failed replacement start
- supervisor tick and bounded foreground supervisor run
- supervisor daemon start/status/stop scaffold
- statefile ownership and process diagnostics
- lifecycle readiness, diagnostics, and runbook projections

The evidence text should cite the stable implementation and verification paths rather than relying on scattered supplemental notes. The boundary text must continue to state that this is not an automatic production recovery guarantee, not live provider availability, not broker/trading readiness, and not a workflow execution layer.

## Test Strategy

Add a focused test to `tests/test_function_tree_registry.py` that parses the real `FUNCTION_TREE.md` and asserts:

- B-16 and E-09 are `[已实现]`.
- Their evidence mentions the core lifecycle control symbols.
- Their boundaries retain non-overclaiming phrases for explicit operator control and non-readiness guarantees.

Run that test before editing `FUNCTION_TREE.md` to confirm the failure is the stale registry status/evidence. After updating the registry, run the focused registry tests plus existing subscription/bridge/CLI tests that prove the cited evidence still works.

## Non-Goals

- No new HTTP route, CLI command, restart policy, provider process manager, or trade behavior.
- No promotion of D-07, D-08, or E-11.
- No claim that subscription watch lifecycle control proves live TongDaXin provider availability, broker readiness, production health, or trading readiness.
