# Change: Catalog Validate Bundle Step Entry Counts

## Why

`catalog validate` reports selected bundle step totals, source counts, name counts, and label counts. For E-11 bundle registry review, callers also need a compact count of which catalog entries are referenced by selected bundle steps, without expanding every bundle or implying execution.

## What Changes

- Add `bundle_step_entry_counts` to `catalog validate` validation payloads.
- Carry `bundle_step_entry_counts` into `catalog validate --view summary`.
- Keep the field derived only from resolved selected bundle step `entry` values.

## Out of Scope

- No task, report, trade, or bundle execution.
- No arbitrary workflow builder.
- No full bundle/step listing or availability proof.
