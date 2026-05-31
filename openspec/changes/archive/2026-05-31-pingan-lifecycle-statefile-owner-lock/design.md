## Context

The current PingAn readiness work deliberately separates read-only status from executable lifecycle control. `dialog_readiness` reports that statefile locking and lifecycle ownership are not yet acquired, and D-07/D-08 remain `[部分实现]`. The next useful step is a local, explicit ownership primitive that can be tested without touching the real PingAn desktop process.

## Goals / Non-Goals

**Goals:**

- Add a deterministic manager method for PingAn lifecycle owner lock `status`, `acquire`, and `release`.
- Store ownership in a caller-provided local statefile plus a sibling `.lock` file.
- Include stable fields for owner token, stale lock detection, paths, and side-effect boundaries.
- Preserve statefile-only side effects and make process-control flags explicitly false.

**Non-Goals:**

- Do not start, stop, restart, kill, supervise, or back off the PingAn desktop process.
- Do not infer ownership from arbitrary OS processes or windows.
- Do not submit orders or write trade event logs, submission ledgers, or trade audit artifacts.
- Do not promote D-07/D-08 to `[已实现]`.

## Decisions

- The caller must provide an `owner_token` for all actions. Blank tokens are rejected.
- `status` is read-only and never writes files.
- `acquire` creates the parent directory, writes a sibling `.lock` file with exclusive create semantics, and writes the lifecycle statefile with `status=owned`.
- `release` requires the same owner token recorded in the statefile, removes the lock file when present, and writes a `status=released` statefile.
- Staleness is derived from the existing statefile timestamp or lock-file mtime relative to `stale_after_seconds`; stale state is reported but not replaced unless the caller explicitly sets `force_stale=True`.
- The result payload always exposes process-control flags as false so downstream registry evidence cannot be mistaken for real lifecycle control.

## Risks / Trade-offs

- A local file lock is not a complete distributed lock. It is acceptable for this slice because the promotion gate needs a deterministic local ownership artifact before process supervision is introduced.
- Requiring a caller-provided path avoids silently writing lifecycle ownership into existing last-order or audit artifacts, but callers must choose and manage the lifecycle statefile location explicitly.
