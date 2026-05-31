## Context

The manager surface `TdxTradeManager.pingan.lifecycle_owner_lock(...)` provides explicit local ownership statefile operations. Operators need a stable CLI path for this promotion gate before higher-risk supervisor and real process lifecycle controls are introduced.

## Goals / Non-Goals

**Goals:**

- Expose `trade lifecycle-owner-lock` as a stable nested trade CLI subcommand.
- Parse action, statefile path, owner token, stale timeout, and forced stale replacement.
- Reuse the existing `TdxTradeManager` construction style and dispatch directly to the manager method.
- Preserve manager payload boundaries in CLI output.

**Non-Goals:**

- Do not add `catalog run` or bundle execution semantics.
- Do not add process start/stop/restart/kill/supervisor/backoff controls.
- Do not submit orders or write trade event/audit artifacts beyond the owner lock manager's local statefile and lock files.
- Do not promote D-07/D-08 to `[已实现]`.

## Decisions

- The CLI command is nested under `trade` because it is part of PingAn desktop trading governance, but its name is explicit enough to avoid order execution ambiguity.
- `--action` defaults to `status`; `--statefile-path` and `--owner-token` are required to avoid implicit writes to unrelated trade artifacts.
- The command uses the existing `--profile`, `--title-key`, `--exe-path`, and `--output` conventions.
- `--force-stale` is only a flag forwarded to the manager; stale replacement remains explicit.

## Risks / Trade-offs

- The CLI makes local ownership writes easier to run, so the command name and required path/token arguments must stay explicit.
- This is still only a local operator primitive. Real PingAn process lifecycle ownership remains a later gate.
