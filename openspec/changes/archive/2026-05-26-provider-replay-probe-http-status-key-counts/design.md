## Context

Provider replay status is a read-only diagnostic surface for replay HTTP fake provider probes. Probe summary already aggregates HTTP status maps for requested, healthy, and failed probes; this change adds map-length fields for compact shape metadata.

## Goals / Non-Goals

**Goals:**

- Derive `requested_http_status_key_count` from `requested_http_status_counts`.
- Derive `healthy_http_status_key_count` from `healthy_http_status_counts`.
- Derive `failed_http_status_key_count` from `failed_http_status_counts`.
- Preserve replay-only, read-only, no-lifecycle-management behavior.

**Non-Goals:**

- Do not request additional probes.
- Do not start sockets, restart services, mutate provider state, or manage daemon lifecycle.
- Do not claim HTTP endpoint coverage, health, readiness, or live provider availability.

## Decisions

- Add the fields in `_build_provider_replay_probe_summary()`.
  - Rationale: the HTTP status maps are built in the same function, so derived key counts can be computed locally without broadening interfaces.
  - Alternative considered: derive fields only in CLI summary view. That would omit detailed status payload consumers and duplicate logic.
- Use `len(<map>)` for the already accumulated maps.
  - Rationale: each key-count field must reflect the projected map keys exactly, including empty maps.

## Risks / Trade-offs

- Risk: readers may treat HTTP status key counts as endpoint coverage or readiness evidence.
  - Mitigation: tests and FUNCTION_TREE boundary state that the fields only count existing diagnostic map keys and do not request probes or control lifecycle.
