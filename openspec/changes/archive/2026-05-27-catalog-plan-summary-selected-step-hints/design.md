## Context

E-11 is the command catalog registry area. The current `plan_summary` already carries the planning boundary and the compact selected-step summary remains available as a sibling. This change moves a small subset of already-known step hints into `plan_summary` itself so the summary surface is easier to read without changing execution behavior.

## Design

Add the following fields to `plan_summary` in `_build_catalog_plan_summary`:

- `first_step_index`
- `last_step_index`
- `first_step_name`
- `last_step_name`
- `first_step_source`
- `last_step_source`
- `first_step_command_name`
- `last_step_command_name`

These fields are copied directly from `selected_step_summary`. If the selected-step summary is missing or incomplete, the fields remain `None`/`null` in the summary projection.

## Boundaries

- Do not execute any catalog entry, bundle step, task step, report step, trade command, or provider call.
- Do not change `selected_step_summary` shape or semantics.
- Do not expose raw manifests, option values, resolved arguments, or workflow-builder internals.
- Do not claim readiness, execution coverage, or approval to run a workflow.
