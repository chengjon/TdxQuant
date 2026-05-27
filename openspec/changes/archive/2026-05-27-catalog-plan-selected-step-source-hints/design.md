# Design: Catalog Plan Selected Step Source Hints

## Context

E-11 remains `[部分实现]`: catalog bundle/task/report composition is represented by fixed runtime JSON presets and non-executing validate/plan summaries, not by an arbitrary workflow builder.
The selected-step summary already carries first/last selected step name and entry hints plus key counts.
It omits first/last source even though each selected step already includes dispatch source metadata in the non-executing plan payload.

## Design

Copy source hints from the first and last selected step dispatch objects into `selected_step_summary`:

- `first_step_source`
- `last_step_source`

If a selected step lacks dispatch source metadata, the field value remains `None`.
The fields must not include full dispatch manifests, resolved argument values, execution results, or side effects.

Tests cover a one-step selected bundle and a multi-step task/report bundle summary.

## Non-Goals

- No new workflow builder.
- No catalog run behavior change.
- No task, report, trade, or bundle step execution.
- No resolved argument values or full dispatch manifests in selected-step summary output.
- No broker readiness, trade safety, or execution coverage claim.
