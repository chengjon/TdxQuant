# Design: Catalog Plan Selected Step Arg Key Summary

## Context

E-11 remains `[部分实现]`: catalog bundle/task/report composition is represented by fixed runtime JSON presets and non-executing validate/plan summaries, not by an arbitrary workflow builder.
Bundle plan summary already exposes:

- `step_resolved_arg_key_count`
- `step_source_resolved_arg_key_count`
- count maps for selected step source/name/entry/resolved-arg keys

The nested `selected_step_summary` currently includes source/name/entry key counts but not resolved-arg key counts.

## Design

Copy the existing top-level count values into `selected_step_summary`:

- `step_resolved_arg_key_count`
- `step_source_resolved_arg_key_count`

The fields are counts only. They must not include resolved argument values, full step manifests, execution results, or dispatch side effects.
They must stay scoped to the selected bundle step slice and match the corresponding sibling summary fields.

Tests cover a one-step selected bundle and a multi-step task/report bundle summary.

## Non-Goals

- No new workflow builder.
- No catalog run behavior change.
- No task, report, trade, or bundle step execution.
- No resolved argument values in summary output.
- No broker readiness, trade safety, or execution coverage claim.
