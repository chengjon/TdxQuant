# Change: PingAn supervisor restart readiness summary

## Why

PingAn lifecycle supervisor can now opt into recorded-PID process restart. After that restart, operators still need a bounded evidence summary that says whether the broker health check recovered or remains unhealthy. Without that summary, the lifecycle registry can show restart execution but not the immediate post-restart readiness outcome.

## What Changes

- Add optional post-restart broker health recheck fields to PingAn lifecycle supervisor tick/run.
- Surface `lifecycle_recovery_status` from the recheck: `recovered`, `still_unhealthy`, `not_requested`, or `not_executed`.
- Add CLI flags for restart recheck opt-in and optional delay.
- Register this as D-07/D-08 partial lifecycle evidence in `FUNCTION_TREE.md`.

## Non-Goals

- No order execution, submit retry, or resubmission.
- No claim that broker health equals trading readiness, UI login readiness, or live/manual acceptance.
- No broad process discovery or bypass of recorded-PID lifecycle process guards.
- No promotion of D-07/D-08 to `[已实现]`.
