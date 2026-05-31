## Context

`promotion_gate_status.lifecycle_owner_lock_status` already provides a read-only preflight owner-lock requirement. The execution path should be able to reuse the same local statefile decision as an explicit safety guard before any desktop automation function is called.

## Goals / Non-Goals

**Goals:**

- Add opt-in local owner-lock requirement checks to PingAn buy/sell/submit-once methods.
- Ensure guard failures happen before desktop automation dispatch.
- Preserve existing idempotency and risk-gate behavior.
- Surface stable rejection metadata under `trade_safety.risk_gate.lifecycle_owner_lock_required_status`.
- Expose the guard through stable CLI execution commands.

**Non-Goals:**

- No default owner-lock requirement.
- No acquire/release behavior in trade execution commands.
- No start/stop/restart/kill/supervise/backoff.
- No claim of real PingAn desktop PID ownership, broker readiness, production readiness, or D-07/D-08 implemented status.

## Decisions

- Reuse `_build_pingan_preflight_lifecycle_owner_lock_status(...)` for the execution guard. That keeps status, staleness, owner-token matching, and PID diagnostics consistent with preflight.
- Embed the guard result in the existing `risk_gate` object. Existing trade audit classification already treats failed risk gates as rejected, which is the right outcome for an opt-in safety guard.
- Thread options through `PingAnDesktopTraderGateway` because stable `trade buy/sell/submit-once` uses the securities gateway path, not direct manager calls.

## Risks / Trade-offs

- Guard failures will write normal rejected trade artifacts through existing finalization. This is intentional audit evidence, but the boundary must state that lifecycle statefile/lock is not written by the guard itself.
- Exposing the guard via CLI could be mistaken for full lifecycle ownership. Mitigation: FUNCTION_TREE and specs state it is local statefile safety evidence only.
