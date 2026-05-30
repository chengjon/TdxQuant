## Context

PingAn `dialog_readiness` is a read-only diagnostic. It can observe runtime/window state and expose non-ownership for statefile/locks, but it does not own or control the PingAn desktop lifecycle. Consumers need a stable lifecycle control status that prevents "window observed" from being confused with "process lifecycle owned."

## Goals / Non-Goals

**Goals:**

- Add `lifecycle_control_status` to `desktop_lifecycle_gate_status`.
- Make all lifecycle-control action flags explicitly false.
- Include the declared process/window inputs that future lifecycle control would use.
- Keep process/window lifecycle ownership in remaining gates until actual control exists.
- Preserve D-07/D-08 partial status semantics in `FUNCTION_TREE.md`.

**Non-Goals:**

- Do not start, stop, restart, kill, or supervise the PingAn desktop process.
- Do not implement restart/backoff, supervisor loops, PID ownership, or owner tokens.
- Do not write order state, event logs, submission ledger entries, or trade audit artifacts.
- Do not mark D-07 or D-08 `[已实现]`.

## Decisions

- Represent lifecycle control as `desktop_lifecycle_gate_status.lifecycle_control_status` rather than changing health checks. This preserves existing dialog readiness pass/fail behavior.
- Use `status=not_owned`, `execution_mode=readonly_lifecycle_control_status`, `control_available=false`, and false execution flags for start/stop/restart/supervisor/backoff.
- Keep `process_window_lifecycle_ownership` in `remaining_lifecycle_gates`. A registry entry is not lifecycle control.

## Risks / Trade-offs

- [Risk] Consumers could treat the existence of this status as lifecycle control. -> The payload explicitly reports no control availability and all action flags false; FUNCTION_TREE records the boundary.
- [Risk] Future real lifecycle control may require a richer schema. -> This change reserves a stable status location with explicit action fields that can later become true only after a separate OpenSpec change.
