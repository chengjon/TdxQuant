## Context

The prior owner-lock slice added explicit local statefile and lock-file writes. The statefile includes `owner_pid`, but callers still need a stable way to distinguish a currently alive local owner process from a stale or malformed owner record.

## Goals / Non-Goals

**Goals:**

- Validate the owner PID recorded in the PingAn lifecycle owner statefile.
- Include stable `owner_pid`, `owner_pid_alive`, `owner_pid_status`, and `pid_validation_executed` fields in owner-lock payloads.
- Keep validation read-only for `status`, and preserve statefile-only side effects for `acquire`/`release`.

**Non-Goals:**

- Do not claim that the recorded PID is the PingAn desktop PID.
- Do not kill, signal for lifecycle control, restart, supervise, or back off any process.
- Do not infer ownership from windows, titles, or broker readiness.
- Do not promote D-07/D-08 to `[已实现]`.

## Decisions

- PID validation uses local process liveness only. On POSIX this is `os.kill(pid, 0)`; permission errors are treated as alive because the process exists.
- Missing or invalid PID values produce `owner_pid_status=missing` and `owner_pid_alive=null`.
- The payload keeps `pid_ownership_claimed=false` even when the recorded owner PID is alive.
- `status` never writes files; `acquire` and `release` still write only the local lifecycle statefile/lock artifacts.

## Risks / Trade-offs

- PID liveness is a local diagnostic and can be subject to PID reuse. It is still useful as a bounded signal because the owner statefile also records owner token and timestamps.
- This does not prove live PingAn readiness. Real process ownership and supervisor controls remain separate promotion gates.
