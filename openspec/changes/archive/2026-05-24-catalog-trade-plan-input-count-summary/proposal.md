## Why

D-07/D-08 catalog plan summary already exposes `trade_plan_boundary` with required, provided, and missing input field lists, but operators must count those lists manually to see whether a plan has full input coverage. Compact counts make the non-executing trade boundary easier to audit without implying live trading readiness.

## What Changes

- Add `required_input_count`, `provided_input_count`, and `missing_input_count` to `trade_plan_boundary`.
- Derive the counts from existing `required_input_fields`, `provided_input_fields`, and `missing_input_fields`.
- Preserve existing field lists, side projection, non-execution metadata, and dispatch behavior.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` D-07/D-08 evidence and boundary text.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: catalog plan/preview trade boundary summaries include compact input coverage counts.

## Impact

- Code: `tdxquant/cli.py`
- Tests: `tests/test_api_cli.py`
- Specs: `openspec/specs/tdx-command-catalog/spec.md`
- Registry: `FUNCTION_TREE.md` remains the single feature/status registry.
