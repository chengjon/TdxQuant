## Context

`_build_provider_replay_probe_summary()` already computes requested status counts, failed status counts, requested reachability counts, requested HTTP status counts, healthy HTTP status counts, error-code counts, and failed error-code counts. It does not yet expose the HTTP status distribution of requested non-healthy probes.

## Goals / Non-Goals

- Add deterministic HTTP status counts for requested non-healthy probes.
- Sort numeric HTTP status keys in ascending numeric order as strings, matching requested and healthy HTTP status count behavior.
- Keep the summary derived solely from normalized probe dictionaries.
- Do not perform additional HTTP requests.
- Do not manage daemon lifecycle, reconnect/backoff, scheduling, process supervision, or provider writes.

## Decisions

- Count only statuses where `probe_status != "healthy"`, the probe was requested, and `http_status` is an integer but not a boolean.
- Return an empty object when no failed HTTP status is present.
- Let existing summary-view projection include the new field by copying the full `probe_summary`.

## Risks / Trade-offs

- This field can be mistaken for complete HTTP failure coverage. The boundary text will state that it only summarizes explicitly requested probes from the current status call.
