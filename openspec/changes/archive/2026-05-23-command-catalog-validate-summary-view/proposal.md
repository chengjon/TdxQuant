# Add Command Catalog Validate Summary View

## Why

`FUNCTION_TREE.md` now treats E-11 task/report combo entries as a partially implemented registry node. The catalog already exposes non-executing validation for fixed runtime JSON entries and bundles, but callers must inspect the detailed validation payload to confirm the high-level counts and non-execution boundary.

Adding an opt-in summary view to `catalog validate` makes the registry evidence easier to consume while keeping the full validation payload available by default.

## What Changes

- Add `catalog validate --view summary`.
- Keep `catalog validate` default output unchanged.
- Attach a reduced `summary_view` projection to validation results that reports selected filters, validation counts, validity, and non-execution status.
- Update E-11 in `FUNCTION_TREE.md` with explicit evidence and boundary for the validate summary projection.

## Impact

- Affected spec: `tdx-command-catalog`
- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Boundary: no task/report/trade/bundle step execution, no runtime JSON schema mutation, no arbitrary workflow builder behavior.
