# Proposal: Catalog Plan Selected Step Command Hints

## Why

`catalog plan --bundle ... --view summary` now exposes selected step first/last source, step name, and entry hints.
Each selected step also has non-executing dispatch `command_name` metadata, but callers must inspect `steps` to see the first/last resolved command names.
Adding command-name hints makes `selected_step_summary` a more complete compact source/name/entry/command view without exposing full dispatch payloads.

## What Changes

- Add `selected_step_summary.first_step_command_name`.
- Add `selected_step_summary.last_step_command_name`.
- Derive both fields from existing selected step dispatch metadata.
- Keep catalog planning non-executing.

## Impact

- Affected spec: `tdx-command-catalog`
- Affected code: catalog plan summary view and CLI tests
