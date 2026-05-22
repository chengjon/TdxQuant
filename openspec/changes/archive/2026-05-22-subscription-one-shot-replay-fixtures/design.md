## Context

Subscription one-shot commands are query-style convenience calls: they open a runtime subscription session, invoke one method once, and close the session. They are distinct from `subscription-watch` foreground runs, background worker control, SSE/event-stream transport, and reconnect/backoff governance.

## Goals / Non-Goals

**Goals:**
- Provide deterministic offline replay for the three one-shot subscription commands.
- Add real `TdxApiManager.runtime.subscription_subscribe/unsubscribe/list` methods so CLI dispatch does not only work under mocks.
- Preserve existing live bridge behavior: live one-shot operations still open a subscription session, call once, and close.
- Keep replay explicit via `--provider-mode replay`.
- Update `FUNCTION_TREE.md` E-01 with precise status, evidence, and boundaries.

**Non-Goals:**
- Do not start or manage a foreground `subscription-watch` run.
- Do not add background worker lifecycle control.
- Do not change SSE/event-stream transport semantics.
- Do not add reconnect/backoff governance or heartbeat freshness evaluation.

## Decisions

- Use three separate built-in JSON fixtures:
  - `subscription-subscribe-success`
  - `subscription-unsubscribe-success`
  - `subscription-list-success`
- Route replay through the same `_dispatch_sync_capability(...)` path as other provider replay capabilities.
- Implement live manager one-shot methods by delegating to `RuntimeApi.subscription_*` wrappers, which already encapsulate session open/call/close behavior.
- Keep E-01 partial unless the remaining foreground/background/transport/governance boundaries are deliberately split or closed elsewhere.

## Risks / Trade-offs

- [Risk] Readers may infer replay support means a long-running subscription loop. -> Mitigation: fixtures and FUNCTION_TREE evidence name one-shot capabilities only.
- [Risk] CLI replay may bypass the manager contract. -> Mitigation: tests assert `TdxApiManager(provider_mode="replay")` construction and manager method dispatch.
- [Risk] Live one-shot behavior could change. -> Mitigation: manager methods delegate to existing `RuntimeApi.subscription_*` wrappers in live mode.
