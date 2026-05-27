## Context

E-11 tracks catalog discovery, validation, and registration surfaces. The planning summary is intended to be a compact read-only registry projection. It already mirrors selected step index/name/source/command metadata, but omits the entry identifiers that define the selected step range.

## Design

Update `_build_catalog_plan_summary` to copy two existing selected-step fields into `plan_summary`:

- `first_step_entry`
- `last_step_entry`

The values come directly from `selected_step_summary`. Missing values remain `None`/`null`, matching the existing summary projection style.

## Boundaries

- Do not execute catalog entries, bundle steps, task commands, report commands, trade commands, or provider calls.
- Do not add arbitrary workflow-builder behavior.
- Do not expose full bundle manifests, full step manifests, option values, or resolved argument values.
- Do not change `selected_step_summary`; only mirror existing fields into `plan_summary`.
- Do not claim broker readiness, trade safety, or execution coverage.
