## Context

B-16 and E-09 both rely on `FUNCTION_TREE.md` being explicit about status, evidence, and boundaries. The detailed subscription long-run status summary already has a machine-readable boundary string:

`advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes`

The compact summary views are intentionally reduced, but they now include enough governance fields that the advisory boundary should travel with them.

## Goals / Non-Goals

Goals:

- Project the existing governance boundary string through HTTP and CLI summary views.
- Keep the projection additive and read-only.
- Continue omitting full governance action lists from compact views.

Non-goals:

- Do not change how governance decisions, reasons, actions, or summaries are computed.
- Do not start, stop, reconnect, back off, restart, or manage subscription processes.
- Do not expose raw `control` or `watch_status` payloads in summary views.

## Decisions

1. Reuse the existing detailed payload field.

   The summary builders will copy `status_summary.governance.boundary` when present. They will not synthesize a new value when the detailed payload omits it.

2. Keep parity between HTTP and CLI summary views.

   `bridge_http.build_bridge_watch_status_summary_result()` and `cli._build_bridge_watch_status_summary_payload()` should project the same governance keys so operators get the same boundary evidence from either surface.

3. Preserve reduced-view constraints.

   The new field is a scalar boundary marker. The summary views still omit raw governance `actions`, raw `control`, and raw `watch_status`.

## Risks / Trade-offs

- Additive scalar output is low compatibility risk.
- Compact summary payloads grow by one field, but the field directly prevents overclaiming governance behavior.

## Migration Plan

No migration is required. Existing detailed and summary commands continue to work.

## Open Questions

None.
