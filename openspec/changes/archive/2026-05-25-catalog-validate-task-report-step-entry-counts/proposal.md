## Why

E-11 tracks fixed task/report bundle combinations through non-executing catalog validation. `catalog validate` now exposes task/report bundle step source, name, and source-name counts, but it still lacks the catalog entry distribution for the same task/report subset.

Adding `task_report_bundle_step_entry_counts` lets maintainers verify which task/report entries are wired into the fixed bundle set without expanding the surface into execution or a workflow builder.

## What Changes

- Add additive `task_report_bundle_step_entry_counts` to `catalog validate` detailed payloads.
- Include the same count map in `catalog validate --view summary`.
- Update tests and `FUNCTION_TREE.md` E-11 evidence/boundary.

## Non-Goals

- No execution of task, report, trade, or bundle steps.
- No new bundle or catalog runtime semantics.
- No full bundle/step detail listing beyond compact aggregate counts.

