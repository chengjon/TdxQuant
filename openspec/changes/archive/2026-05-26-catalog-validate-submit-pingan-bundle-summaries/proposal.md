# catalog validate submit/PingAn bundle summaries

## Why

Catalog validation summary views already expose submit-once and PingAn bundle counts, key-count siblings, and bounded samples. Consumers that only need compact status metadata for these two E-11 subsets currently have to read many sibling fields and reconstruct a rollup themselves.

Adding `submit_once_bundle_summary` and `pingan_bundle_summary` keeps the `FUNCTION_TREE.md` evidence compact and explicit while preserving the catalog validation boundary: it summarizes existing validation metadata only and does not execute catalog entries, tasks, reports, trades, or bundle steps.

## What Changes

- Add read-only `submit_once_bundle_summary` to `catalog validate --view summary`.
- Add read-only `pingan_bundle_summary` to `catalog validate --view summary`.
- Derive both objects from existing submit-once/PingAn bundle summary sibling fields:
  - bundle count and resolved step count
  - bounded sample metadata
  - label/source/name/entry/option key counts
- Preserve existing sibling fields for compatibility.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused pytest for API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
