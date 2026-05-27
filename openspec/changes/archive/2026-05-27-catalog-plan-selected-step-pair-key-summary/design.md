## Context

E-11 governs catalog discovery and plan/validation registration. The selected-step rollup already carries selected range hints, source/name/entry key counts, and resolved-arg key counts. Top-level plan summary also exposes `step_source_name_key_count` and `step_source_entry_key_count`, but the selected-step rollup omits those pair-key counts.

## Design

Update `_build_catalog_selected_step_summary` to copy these already-derived top-level summary fields into `selected_step_summary`:

- `step_source_name_key_count`
- `step_source_entry_key_count`

The values remain counts only. The change does not expose full manifests, step payloads, option values, or resolved argument values.

## Boundaries

- Do not execute catalog entries, bundle steps, task commands, report commands, trade commands, or provider calls.
- Do not add workflow-builder behavior.
- Do not expose full bundle manifests, full step manifests, option values, or resolved argument values.
- Do not change step selection behavior; only mirror existing pair-key counts into the selected-step summary.
- Do not claim broker readiness, trade safety, or execution coverage.
