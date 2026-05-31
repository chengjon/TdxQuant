# Change: PingAn supervisor process restart control

## Why

PingAn lifecycle supervisor currently records restart/backoff decisions in the lifecycle statefile. PingAn process lifecycle control can independently restart only a recorded owner-matched PID. The remaining integration gap is that an operator-managed supervisor tick cannot yet opt into executing the recorded-PID restart when the restart/backoff policy allows it.

This change wires those two controls together while preserving the default non-process behavior.

## What Changes

- Add opt-in process restart fields to PingAn lifecycle supervisor tick/run.
- When broker health is unhealthy and the supervisor policy reaches an eligible restart point, optionally call the existing recorded-PID guarded `lifecycle_process(action=restart)`.
- Add CLI flags on `trade lifecycle-supervisor-tick` and `trade lifecycle-supervisor-run` for process restart opt-in and process executable selection.
- Register the evidence in D-07/D-08 in `FUNCTION_TREE.md` without promoting either node to `[已实现]`.

## Non-Goals

- No process restart unless the caller explicitly opts in.
- No broad process discovery, unrelated PID kill, or bypass of `lifecycle_process` recorded-PID guards.
- No order execution, task/report/catalog workflow execution, retry/resubmit, broker readiness claim, UI login readiness claim, or live/manual acceptance claim.
