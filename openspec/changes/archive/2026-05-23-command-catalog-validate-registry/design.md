# Design: Command Catalog Registry Validation

## Context

The catalog resolver already normalizes entries and bundles. `catalog plan` can
resolve a single target without execution, while `catalog list` can enumerate
filtered rows. A registry validation command should reuse those existing
resolvers instead of introducing a parallel interpretation of the JSON files.

## Decisions

### Non-Execution Validation Command

Add `catalog validate` with filters:

- `--kind entry|bundle|all`
- `--entry <name>`
- `--bundle <name>`
- `--label <label>`

The command loads `runtime/command-catalog.json` and, when bundles are selected,
`runtime/command-bundles.json`. It resolves every selected entry or bundle and
collects errors instead of running any step.

### Coverage Summary

The result includes:

- selected filters
- `entry_count`
- `bundle_count`
- `task_report_bundle_count`
- `invalid_count`
- `valid`
- `errors`

`task_report_bundle_count` counts selected bundles whose resolved steps include
at least one `task` source and at least one `report` source.

### Failure Semantics

If any selected target fails validation, the command returns `INVALID_REQUEST`
with `valid=false` and the structured error list in `data`. Successful validation
returns `OK`.

## Risks

- Since `_handle_catalog_subcommand` is a broad CLI dispatch function, regressions
  could affect many catalog tests. Mitigation: keep the change additive and run
  the focused `tests/test_api_cli.py` suite.
