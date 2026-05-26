## Context

Provider replay status is a read-only diagnostic surface for replay HTTP fake provider probes. Probe summary already aggregates error-code and compact error-sample maps; this change adds map-length fields so consumers can inspect diagnostic shape without reading full samples.

## Goals / Non-Goals

**Goals:**

- Derive `error_code_key_count` from `error_code_counts`.
- Derive `failed_error_code_key_count` from `failed_error_code_counts`.
- Derive `error_sample_status_key_count` from `error_sample_status_counts`.
- Derive `error_sample_probe_key_count` from `error_sample_probe_counts`.
- Preserve replay-only, read-only, no-lifecycle-management behavior.

**Non-Goals:**

- Do not request additional probes.
- Do not expose full error payloads or raw probe payloads.
- Do not start sockets, restart services, mutate provider state, or manage daemon lifecycle.
- Do not claim failure coverage completeness, health, readiness, or live provider availability.

## Decisions

- Add the fields in `_build_provider_replay_probe_summary()`.
  - Rationale: the error maps are built in the same function, so derived key counts can be computed locally without broadening interfaces.
  - Alternative considered: derive fields only in CLI summary view. That would omit detailed status payload consumers and duplicate logic.
- Use `len(<map>)` for the already accumulated maps.
  - Rationale: each key-count field must reflect the projected map keys exactly, including empty maps.

## Risks / Trade-offs

- Risk: readers may treat key counts as full failure coverage or raw error detail.
  - Mitigation: tests and FUNCTION_TREE boundary state that the fields only count existing diagnostic map keys and do not expose full payloads or control lifecycle.
