## Why

`catalog plan --view summary` exposes selected step count and step composition maps, but callers still have to inspect the bounded `steps` list to identify the selected step window and first/last selected steps. A compact selected-step summary keeps that information visible without turning the catalog into a workflow runner.

## What Changes

- Add additive `selected_step_summary` metadata to catalog bundle plan/preview summary views.
- Derive it from existing selected-step fields, computed step count maps, and bounded plan step views.
- Keep it read-only and non-executing: it must not execute catalog entries, bundles, task/report steps, trade commands, provider calls, or workflow actions.

## Impact

- Affected spec: `tdx-command-catalog`
- Affected code: catalog summary projection, focused CLI tests, and `FUNCTION_TREE.md` E-11 registry evidence/boundary.
