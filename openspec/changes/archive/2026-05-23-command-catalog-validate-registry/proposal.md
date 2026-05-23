# Add Command Catalog Registry Validation

## Why

`runtime/command-catalog.json` and `runtime/command-bundles.json` are now the
fixed registry for many task/report follow-up combinations. Operators can list
and plan bundles, but there is no explicit non-execution command that validates
all selected entries and bundles resolve cleanly and reports the current bundle
coverage counts.

## What Changes

- Add `catalog validate` as a non-execution CLI subcommand.
- Validate selected catalog entries and bundles by resolving them through the
  existing registry loaders and bundle resolver.
- Return compact counts, including task/report combination bundle coverage.
- Support the same target filters as catalog listing: `--kind`, `--entry`,
  `--bundle`, and `--label`.
- Update tests and `FUNCTION_TREE.md` E-11 evidence/boundary.

## Out of Scope

- Executing tasks, reports, trades, or bundles.
- Creating arbitrary workflow-builder semantics.
- Changing existing `catalog list`, `catalog plan`, `catalog preview`, or
  `catalog run` behavior.
- Validating that referenced runtime presets are safe to execute in a live
  environment beyond the existing resolver metadata checks.

## Impact

- Affected spec: `tdx-command-catalog`
- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
