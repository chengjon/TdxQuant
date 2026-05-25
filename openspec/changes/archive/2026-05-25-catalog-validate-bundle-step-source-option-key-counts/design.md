## Design

Extend the existing catalog validation counting loop. When a resolved bundle step has a string `source` and a dict `options`, increment `bundle_step_source_option_key_counts[f"{source}:{option_key}"]` for each non-empty string option key.

The count is selected-bundle scoped, just like `bundle_step_option_key_counts`, `bundle_step_source_counts`, and `bundle_step_source_name_counts`. The summary view copies the aggregate map from validation output.

## Boundaries

- The field is a count map only; it does not expose option values or full step manifests.
- It does not execute catalog entries, task/report commands, trades, or bundle steps.
- It is not a workflow builder, execution coverage proof, or readiness signal.

