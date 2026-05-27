# Proposal: Catalog Plan Selected Step Source Hints

## Why

`catalog plan --bundle ... --view summary` includes a compact `selected_step_summary` with first/last selected step names and entries.
The same selected step payload already has dispatch source metadata, but the summary does not expose first/last source hints.
Consumers that want a compact source/name/entry summary must inspect `steps`.

## What Changes

- Add `selected_step_summary.first_step_source`.
- Add `selected_step_summary.last_step_source`.
- Derive both fields from existing selected step dispatch metadata.
- Keep catalog planning non-executing.

## Impact

- Affected spec: `tdx-command-catalog`
- Affected code: catalog plan summary view and CLI tests
