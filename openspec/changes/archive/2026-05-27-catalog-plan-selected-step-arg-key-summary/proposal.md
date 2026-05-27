# Proposal: Catalog Plan Selected Step Arg Key Summary

## Why

`catalog plan --bundle ... --view summary` already computes top-level selected-step resolved-argument key counts.
The nested `selected_step_summary` is the compact place consumers use for selected-step metadata, but it omits the resolved-arg key counts and source-qualified resolved-arg key counts.
Callers must read sibling fields instead of getting a self-contained selected-step summary.

## What Changes

- Add `selected_step_summary.step_resolved_arg_key_count`.
- Add `selected_step_summary.step_source_resolved_arg_key_count`.
- Derive both fields from existing top-level summary counts without exposing resolved argument values.
- Keep catalog planning non-executing.

## Impact

- Affected spec: `tdx-command-catalog`
- Affected code: catalog plan summary view and CLI tests
