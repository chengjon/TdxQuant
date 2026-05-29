## Context

The current background controller already writes `active.json`, `pid`, and a flock-backed `lock` path. Recent lifecycle slices rely on these files for restartability and supervisor tick recovery, but status diagnostics do not expose whether the control state and owned pidfile still agree.

## Goals / Non-Goals

**Goals:**

- Provide a deterministic `statefile_ownership` payload on controller status.
- Report whether the active statefile exists, whether the pidfile exists, whether the active payload PID matches the owned pidfile, and whether the referenced PID is alive.
- Include a stable schema version, status, reason codes, and boundary string.
- Surface the compact diagnostic in bridge diagnostics view.

**Non-Goals:**

- No new start/stop/restart behavior.
- No daemon loop, timer, scheduler, or background supervisor.
- No control-lock acquisition from diagnostics.
- No port probing, provider health proof, Windows provider lifecycle management, or readiness guarantee.
- No exposure of raw file paths or raw active/watch payload through diagnostics view.

## Decisions

- Keep the ownership diagnostic in `subscription_watch_background.py`, near the existing statefile helpers, because it needs the existing path model and PID parser.
- Treat `owned_active` as the only positive ownership state: the control payload is active, the payload PID matches the pidfile, and the PID is alive.
- Treat missing statefile as `not_present`, inactive terminal state as `terminal`, and active mismatches/dead PID as `mismatch`.
- Add diagnostics projection in `subscription_watch_status_diagnostics.py` by copying the compact status payload field, keeping bridge diagnostics reduced and non-raw.

## Risks / Trade-offs

- [Risk] PID liveness is only a local OS signal. -> The boundary string explicitly says this does not prove provider readiness or production ownership.
- [Risk] Diagnostics could be mistaken for lifecycle control. -> The payload is read-only and no endpoint/CLI command changes behavior.
- [Risk] Existing `status()` reconciles stale state before diagnostics. -> The diagnostic describes the reconciled local state visible to callers, not a raw forensic dump.

