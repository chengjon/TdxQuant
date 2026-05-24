# Change: Catalog Validate Bundle Step Name Counts

## Why

`catalog validate` already reports selected bundle step totals, step source counts, and label counts. For E-11 task/report bundle registry work, readers also need a compact view of selected bundle step name composition, without expanding every bundle or implying any step was executed.

## What Changes

- Add `bundle_step_name_counts` to `catalog validate` validation payloads.
- Carry `bundle_step_name_counts` into `catalog validate --view summary`.
- Keep the field derived only from resolved selected bundle definitions.

## Out of Scope

- No task, report, trade, or bundle execution.
- No arbitrary workflow builder.
- No full bundle/step listing or availability proof.
