## Context

E-11 tracks catalog discovery, validation, and registration. `plan_summary` is the compact top-level planning registry, and it already mirrors selected step range, first/last hints, entry hints, and several key counts. It should also mirror the source-pair key counts now present in `selected_step_summary`.

## Design

Update `_build_catalog_plan_summary` to copy these already-derived fields from `selected_step_summary`:

- `step_source_name_key_count`
- `step_source_entry_key_count`

The fields remain counts only. They do not expose full manifests, step payloads, option values, or resolved argument values.

## Boundaries

- Do not execute catalog entries, bundle steps, task commands, report commands, trade commands, or provider calls.
- Do not add workflow-builder behavior.
- Do not expose full bundle manifests, full step manifests, option values, or resolved argument values.
- Do not change step selection behavior; only mirror existing source-pair counts into the planning summary.
- Do not claim broker readiness, trade safety, or execution coverage.
