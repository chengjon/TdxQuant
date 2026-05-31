## Context

`trade preflight` already checks PingAn broker runtime health through `PingAnBrokerAdapter.health_check()`. The side-effecting `confirm_current` path has owner-lock guard support, but it does not have a direct broker readiness guard before attempting to locate or click the current confirmation dialog.

This slice adds the smallest useful broker readiness control to the manual confirmation path. It keeps the guard opt-in so existing scripted confirm-current flows remain compatible.

## Goals / Non-Goals

**Goals:**

- Add `require_broker_readiness` to `TdxTradeManager.pingan.confirm_current(...)`.
- Reject before confirm dialog lookup/click when broker readiness is required and `PingAnBrokerAdapter.health_check()` fails.
- Forward the option through stable `trade confirm-current` and `task trade-confirm-current`.
- Register D-07 evidence without status promotion.

**Non-Goals:**

- No default behavior change when `require_broker_readiness` is omitted.
- No broker process start/stop/restart/supervision.
- No retry/backoff/recovery/resubmission.
- No live/manual acceptance claim.
- No D-08 submit-once or buy/sell coverage in this slice.

## Decisions

- Reuse `PingAnBrokerAdapter.health_check()` as the guard source.
  - Rationale: it is the same broker runtime evidence used by `trade health` and `trade preflight`.
  - Alternative considered: require callers to run `trade preflight` separately and pass a token. Rejected because it would not guard the actual confirm-current invocation.

- Evaluate broker readiness before confirm dialog lookup.
  - Rationale: a failed required broker readiness check must prevent desktop UI lookup/click side effects.
  - Alternative considered: attach readiness status after the click. Rejected because it would not be a guard.

- Keep task and CLI layers as pass-through.
  - Rationale: broker readiness evaluation belongs in the PingAn manager where the title/exe context already lives.

## Risks / Trade-offs

- [Risk] Broker health can be transient and reject a confirmation that an operator intended to run. -> Mitigation: guard is opt-in and failure includes the broker health result plus next action.
- [Risk] Users may confuse this with full broker readiness. -> Mitigation: FUNCTION_TREE and specs keep D-07 partial and state this is broker runtime health only.
