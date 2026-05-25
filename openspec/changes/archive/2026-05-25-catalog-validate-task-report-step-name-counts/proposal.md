## Why

`FUNCTION_TREE.md` keeps E-11 task/report combo entries as partial while the command catalog registry gains explicit evidence for fixed runtime bundles. `catalog validate` already reports task/report bundle counts and source counts, but it does not expose the step-name mix inside those task/report bundles.

Adding `task_report_bundle_step_name_counts` makes the task/report combo structure auditable without executing task, report, trade, or bundle steps.

## What Changes

- Add additive `task_report_bundle_step_name_counts` to `catalog validate` detailed payloads.
- Include the same count map in `catalog validate --view summary`.
- Update tests and `FUNCTION_TREE.md` E-11 evidence/boundary.

## Non-Goals

- No execution of task, report, trade, or bundle steps.
- No new bundle or catalog runtime semantics.
- No full bundle/step detail listing beyond compact aggregate counts.
