## Context

Provider replay status is a read-only diagnostic surface for the replay HTTP fake provider. Probe summary already aggregates probe status maps; this change adds map-length fields to make the compact summary easier to consume consistently.

## Goals / Non-Goals

**Goals:**

- Derive `status_key_count` from `status_counts`.
- Derive `requested_status_key_count` from `requested_status_counts`.
- Derive `failed_status_key_count` from `failed_status_counts`.
- Preserve replay-only, read-only, no-lifecycle-management behavior.

**Non-Goals:**

- Do not request additional probes.
- Do not start sockets, restart services, mutate provider state, or manage daemon lifecycle.
- Do not claim health, readiness, endpoint coverage, or live provider availability.

## Decisions

- Add the fields in `_build_provider_replay_probe_summary()`.
  - Rationale: the count maps are built in the same function, so derived key counts can be computed locally without broadening call signatures.
  - Alternative considered: derive fields only in CLI summary view. That would omit the detailed status payload and make HTTP/manager consumers recompute the same values.
- Use `len(<map>)` after sorted map construction.
  - Rationale: key-count fields should exactly reflect the projected map keys, including empty maps.

## Risks / Trade-offs

- Risk: readers may treat key counts as health or readiness evidence.
  - Mitigation: tests and FUNCTION_TREE boundary state that the fields only count existing diagnostic map keys and do not request probes or control lifecycle.
