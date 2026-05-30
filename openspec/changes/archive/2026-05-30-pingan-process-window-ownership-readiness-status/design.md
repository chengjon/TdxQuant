## Context

PingAn `dialog_readiness` already returns `desktop_lifecycle_gate_status` with dialog lookup checks and declared process/window ownership inputs. The actual process/window lifecycle ownership gate is still incomplete because the workflow does not manage a process, own a statefile lock, supervise lifecycle, or restart/backoff.

## Goals / Non-Goals

**Goals:**

- Add an observed, read-only process/window ownership status to `desktop_lifecycle_gate_status`.
- Reuse `PingAnBrokerAdapter.health_check()` so the signal uses the existing runtime and main-window discovery contract.
- Keep dialog readiness overall status driven by dialog checks only; process/window observation is lifecycle evidence, not an execution precondition for this command.
- Preserve D-07/D-08 partial status semantics in `FUNCTION_TREE.md`.

**Non-Goals:**

- Do not start, stop, restart, or supervise the PingAn desktop process.
- Do not add statefile ownership, lock ownership, PID ownership, or backoff policy.
- Do not submit orders, close dialogs, or click controls.
- Do not mark D-07 or D-08 `[已实现]`.

## Decisions

- Add a separate `observed_process_window_ownership` field under `desktop_lifecycle_gate_status` instead of adding it to the health `checks` list. This records lifecycle evidence without changing dialog readiness pass/fail semantics.
- Store the full serialized health result plus normalized summary fields (`runtime_ok`, `window_ok`, `status`, `title_keyword`, `exe_path`) so consumers can inspect the observation without relying on message text.
- Keep `process_window_lifecycle_ownership` in remaining lifecycle gates. A read-only observation is not lifecycle control.

## Risks / Trade-offs

- [Risk] Runtime/window health can be unavailable on non-Windows or headless environments. -> Report `status=unverified` with the serialized health result and do not fail dialog readiness solely from this observation.
- [Risk] Consumers could treat observed window status as owned lifecycle. -> Boundary text and FUNCTION_TREE notes state that process ownership, statefile lock, supervisor, restart/backoff, and live/manual acceptance remain out of scope.
