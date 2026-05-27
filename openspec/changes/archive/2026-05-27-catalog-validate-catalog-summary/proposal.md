# catalog validate catalog summary

## Why

`catalog validate --view summary` now exposes compact outcome, entry, bundle, label, and source rollups. Consumers that need a single registry status object still have to read several sibling objects and reconstruct the top-level validation picture themselves.

Adding `catalog_summary` gives E-11 a stable read-only top-level view for catalog discovery and validation while keeping the boundary narrow: it summarizes already projected validation metadata only and must not execute catalog entries, tasks, reports, trades, provider calls, or bundle steps.

## What Changes

- Add read-only `catalog_summary` to `catalog validate --view summary`.
- Derive the object from existing validation outcome, entry, bundle, label, and source summary fields.
- Include selected filters, validity, non-execution marker, entry/bundle counts, bundle-step count, distinct label/source key counts, and high-level presence flags.
- Preserve existing sibling fields and compact summary objects for compatibility.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused pytest for API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
