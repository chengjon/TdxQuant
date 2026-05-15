## Why

The catalog already lists and plans entries/bundles, but discovery output does not expose enough machine-readable preview metadata for callers to understand matched labels, selected bundle ranges, and non-executing previews. This package hardens discovery without changing the catalog schema or making catalog entries define business contracts.

## What Changes

- Add explicit discovery metadata to catalog list output, including matched label summaries for entries and bundles.
- Add a non-executing `catalog preview` command that mirrors `catalog plan` semantics while clearly reporting preview mode.
- Tighten summary-view output for list/plan/preview so consumers get stable, reduced fields instead of relying on detailed execution payloads.
- Add focused tests for label discovery, bundle discovery, preview dispatch, and summary output constraints.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-command-catalog`: Adds discovery/preview output constraints for the existing command catalog CLI without changing catalog JSON schema.

## Impact

- Affected code: `tdxquant/cli.py`, focused CLI/catalog tests, and `FUNCTION_TREE.md`.
- Affected specs: `tdx-command-catalog`.
- No dependency changes.
- No changes to `runtime/command-catalog.json` or `runtime/command-bundles.json` schema.
