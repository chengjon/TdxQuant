# Design: Catalog Plan Selected Step Index Hints

## Context

E-11 remains `[部分实现]`: catalog bundle/task/report composition is represented by fixed runtime JSON presets and non-executing validate/plan summaries, not by an arbitrary workflow builder.
The selected-step summary carries first/last selected step source, command, name, and entry hints.
It omits first/last selected step indexes, even though the selected plan steps already expose them.

## Design

Copy index hints from the first and last selected plan step objects into `selected_step_summary`:

- `first_step_index`
- `last_step_index`

If a selected step lacks index metadata, the field value remains `None`.
The fields must not include full step manifests, dispatch manifests, resolved argument values, execution results, or side effects.

Tests cover a one-step selected bundle and a multi-step task/report bundle summary.

## Non-Goals

- No new workflow builder.
- No catalog run behavior change.
- No task, report, trade, or bundle step execution.
- No resolved argument values, full step manifests, or full dispatch manifests in selected-step summary output.
- No broker readiness, trade safety, or execution coverage claim.
