## Context

`TdxRuntimeSubscriptionSession` already wraps the live TongDaXin runtime subscription methods:

- `subscribe_hq(stock_list, callback)`
- `unsubscribe_hq(stock_list)`
- `get_subscribe_hq_stock_list()`

Higher-level subscription work currently focuses on foreground `task subscription-watch`, worker bridge control-plane operations, and event-stream transport. A query-style one-shot CLI should be narrower: open a runtime subscription session, invoke exactly one subscription method, return its result and session metadata, then close the session.

## Goals / Non-Goals

**Goals:**

- Provide one-shot API wrappers for subscribe, unsubscribe, and list operations.
- Expose those wrappers under the query-style `api` CLI namespace.
- Include operation metadata so callers can distinguish one-shot commands from watch runs.
- Reject replay mode explicitly until subscription one-shot replay fixtures exist.

**Non-Goals:**

- Do not change `task subscription-watch`, worker bridge commands, background controller state, or SSE stream contracts.
- Do not keep a process alive to consume subscription events.
- Do not add reconnect/backoff/watermark governance.
- Do not add new provider fixture schemas for one-shot subscription operations in this package.

## Decisions

1. Implement wrappers in `tdxquant/api/bridge.py` and expose them through `RuntimeApi`.
   - Rationale: the underlying runtime methods already live in `TdxRuntimeSubscriptionSession`; keeping wrappers nearby avoids duplicating low-level runtime loading logic.
   - Alternative considered: route through `TdxTaskManager.subscription_watch`. Rejected because `subscription-watch` is a bounded run artifact workflow, not a one-shot query-style method call.

2. Add `api subscription-subscribe`, `api subscription-unsubscribe`, and `api subscription-list`.
   - Rationale: the gap is explicitly query-style one-shot CLI, and existing query-style commands live under `api`.
   - Alternative considered: add `task subscription-*` commands. Rejected because task commands imply workflow/artifact semantics already covered by `subscription-watch`.

3. Use a no-op callback for one-shot subscribe.
   - Rationale: the runtime method requires a callback argument, but the CLI command must not become a long-running event consumer.
   - Alternative considered: expose callback configuration. Rejected because it belongs to `subscription-watch` or worker bridge flows.

## Risks / Trade-offs

- A one-shot subscribe may not be useful after process exit in all runtime environments -> The payload must identify `mode=one_shot` and avoid claiming a persistent watcher is running.
- Users may expect replay mode because other API commands support it -> Replay mode remains rejected until dedicated one-shot subscription fixtures are introduced.
- Subscription one-shot commands may be confused with SSE/provider transport -> The spec and FUNCTION_TREE boundary explicitly exclude event streaming and long-running transport.

## Migration Plan

No migration is required. Existing subscription-watch, bridge, and task commands continue unchanged.

## Open Questions

- Dedicated replay fixtures for one-shot subscription operations remain a future package.
- Durable subscription state across CLI process boundaries remains outside this package.
