# Change: PingAn lifecycle supervisor control

## Why

D-07 and D-08 already have PingAn trade entrypoints, broker readiness guards, local lifecycle owner locks, and read-only lifecycle readiness summaries. The remaining lifecycle gap is that the local owner lock cannot yet drive a controlled supervisor tick/run loop that observes broker health, records restart/backoff decisions, and writes those decisions into the PingAn lifecycle statefile.

This change adds the first bounded, operator-owned PingAn lifecycle control loop. It is intentionally scoped to local lifecycle governance and evidence registration. It does not execute orders, change buy/sell/submit-once semantics, or claim production trading readiness.

## What Changes

- Add PingAn lifecycle supervisor tick management that requires an owned local lifecycle statefile before any control decision.
- Add bounded restart/backoff state recording driven by broker health observations.
- Add a bounded foreground supervisor run wrapper over repeated ticks.
- Expose explicit `trade lifecycle-supervisor-tick` and `trade lifecycle-supervisor-run` CLI entrypoints.
- Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary to register this as partial lifecycle control evidence.

## Non-Goals

- No automatic order execution, retry, recovery, or resubmission.
- No `catalog run` workflow execution and no task/report/bundle workflow builder changes.
- No OS-level PingAn process kill/start ownership in this slice.
- No promotion of D-07/D-08 to `[已实现]` unless all remaining live/manual acceptance and desktop lifecycle gates are independently closed.
