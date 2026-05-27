# catalog validate source summary

## Why

`catalog validate --view summary` already exposes entry source counts and bundle-step source counts. Consumers that need a compact source-oriented registry view currently have to inspect separate sibling maps and key-count fields.

Adding `source_summary` gives E-11 a stable read-only source rollup for catalog discovery and validation while keeping the boundary narrow: it summarizes already projected catalog metadata only and must not execute catalog entries, tasks, reports, trades, provider calls, or bundle steps.

## What Changes

- Add read-only `source_summary` to `catalog validate --view summary`.
- Derive the object from existing `entry_source_counts`, `entry_source_key_count`, `bundle_step_source_counts`, and `bundle_step_source_key_count` fields.
- Include total distinct source key count across projected entry and bundle-step source maps.
- Preserve existing sibling fields for compatibility.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused pytest for API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
