## Why

The plan/preview `--side` override is intended for single catalog entry previews. During follow-up verification, bundle planning showed that the top-level side override can leak into side-specific bundle steps and make a `sell-submit-once` bundle appear as buy.

That is misleading in the FUNCTION_TREE registry: side-specific bundle definitions must remain authoritative during non-executing bundle planning.

## What Changes

- Prevent top-level catalog plan/preview `--side` from overriding bundle step side metadata.
- Preserve entry-level `--side` overrides for direct/generic submit-once entries.
- Add regression coverage for side-specific sell submit-once bundles.
- Update `FUNCTION_TREE.md` D-08 boundary.

## Capabilities

### New Capabilities

- `tdx-command-catalog`: enforce side ownership boundaries for submit-once bundle plan/preview summaries.

### Modified Capabilities

- None.

## Impact

- CLI bundle planning: `tdxquant/cli.py`
- Tests: `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`

