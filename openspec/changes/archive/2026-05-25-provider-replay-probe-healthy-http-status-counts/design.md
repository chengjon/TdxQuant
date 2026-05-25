## Context

`_build_provider_replay_probe_summary()` already computes global requested status counts, requested reachability counts, requested HTTP status counts, failed status counts, error-code counts, and failed error-code counts. The status summary is read-only and is also projected through the CLI summary view.

## Goals / Non-Goals

- Add deterministic HTTP status counts for healthy requested probes.
- Sort numeric HTTP status keys in ascending numeric order as strings, matching requested HTTP status count behavior.
- Keep the summary derived solely from normalized probe dictionaries.
- Do not perform additional HTTP requests.
- Do not manage daemon lifecycle, reconnect/backoff, scheduling, process supervision, or provider writes.

## Decisions

- Count only statuses where `probe_status == "healthy"` and `http_status` is an integer but not a boolean.
- Return an empty object when no healthy HTTP status is present.
- Let existing summary-view projection include the new field by copying the full `probe_summary`.

## Risks / Trade-offs

- This field can be mistaken for a service-level availability guarantee. The boundary text will state that it only summarizes explicitly requested probes from the current status call.
