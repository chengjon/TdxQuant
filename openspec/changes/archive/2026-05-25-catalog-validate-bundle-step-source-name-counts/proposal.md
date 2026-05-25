## Why

`FUNCTION_TREE.md` keeps E-11 task/report combo entries as partial while the command catalog registry gains explicit read-only evidence for fixed runtime bundles. `catalog validate` already reports selected bundle step source, name, and entry counts separately, but it does not expose a compact combined source/name count.

Adding `bundle_step_source_name_counts` makes the task/report step mix easier to audit without executing any bundle step or implying arbitrary workflow-builder support.

## What Changes

- Add additive `bundle_step_source_name_counts` to `catalog validate` detailed payloads for selected resolved bundles.
- Include the same count map in `catalog validate --view summary`.
- Update tests and `FUNCTION_TREE.md` E-11 evidence/boundary.

## Non-Goals

- No task, report, trade, or bundle execution.
- No new catalog entry or bundle runtime semantics.
- No full bundle/step/detail listing beyond compact aggregate counts.
