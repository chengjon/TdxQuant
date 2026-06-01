## Why

`tdxquant/cli.py` now owns catalog parser construction, list/plan/validate helpers, summary rendering, and command dispatch in one large module. Deepening the catalog CLI boundary will reduce future catalog change friction while preserving the existing read-only catalog behavior.

## What Changes

- Move catalog command registration and handling behind a dedicated catalog CLI command boundary.
- Preserve the existing `catalog list`, `catalog plan`, `catalog preview`, `catalog validate`, and `catalog run` command semantics.
- Keep this change read-only for `list`, `plan`, `preview`, and `validate`; it MUST NOT execute task/report/trade/bundle steps except through the existing `catalog run` path.
- Add behavior tests that exercise the public CLI parser/handler surface rather than private implementation details.
- Update `FUNCTION_TREE.md` evidence for the CLI/catalog architecture boundary after implementation.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: catalog CLI commands gain an explicit command boundary while preserving existing catalog discovery, validation, planning, preview, and run behavior.

## Impact

- Affected code: `tdxquant/cli.py`, new catalog CLI boundary module under `tdxquant/cli/` or an equivalent local package.
- Affected tests: focused catalog CLI tests in `tests/test_api_cli.py` or a newly split catalog CLI test file.
- Affected docs/evidence: `FUNCTION_TREE.md`, archived OpenSpec change, and `tdx-command-catalog` spec.
- No catalog JSON schema change.
- No task, report, trade, provider, or bundle execution semantics change.
