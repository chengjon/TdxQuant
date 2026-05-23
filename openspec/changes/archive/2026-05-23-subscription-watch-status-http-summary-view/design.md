# Design: Bridge Watch Status HTTP Summary View

## Context

The bridge HTTP status endpoint already forwards explicit heartbeat and watermark
staleness thresholds to `SubscriptionWatchBackgroundController.status()`. The CLI
can request a compact summary by transforming the detailed envelope after the
existing bridge request returns.

## Decisions

### Opt-In Query Parameter

`GET /bridge/v1/watch/status?view=summary` returns a compact bridge success
envelope. Missing `view` and `view=detailed` preserve the existing detailed
result exactly. Any unsupported `view` value returns the existing bridge invalid
request failure path.

### Local Projection

The HTTP handler builds the summary from the controller status result it already
received. It does not call additional controller methods and does not mutate the
raw controller result.

The summary result contains:

- `mode=summary`
- `worker`
- `status`
- selected `status_summary` fields: `overall_status`, `heartbeat`, `watermark`,
  and `reconnect`
- selected `governance` fields: `decision`, `requires_manual_review`, and
  `action_summary`

### Preserve Advisory Boundary

The summary is a projection only. It does not trigger reconnect, backoff, restart,
start/stop, SSE, or event-stream behavior.

## Risks

- A remote caller may expect `view=summary` to reduce controller work. Mitigation:
  document and test that it uses the same controller `status()` call and only
  transforms the response payload.
