# Proposal: Catalog Plan Selected Step Index Hints

## Why

`catalog plan --bundle ... --view summary` includes selected step ranges and first/last step identity hints.
Each selected step already carries a stable `index`, but `selected_step_summary` does not expose the first and last selected indexes.
Consumers must inspect `steps` to map the compact summary back to the original bundle ordering.

## What Changes

- Add `selected_step_summary.first_step_index`.
- Add `selected_step_summary.last_step_index`.
- Derive both fields from existing selected step metadata.
- Keep catalog planning non-executing.

## Impact

- Affected spec: `tdx-command-catalog`
- Affected code: catalog plan summary view and CLI tests
