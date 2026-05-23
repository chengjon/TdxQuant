## Why

`provider-replay config-check` already validates replay fake-provider configuration without opening a socket, but its output is only the detailed config summary. E-06 needs the feature registry to distinguish usable read-only inspection surfaces from unavailable daemon lifecycle management, so config validation needs an explicit summary view with those boundaries.

## What Changes

- Add an opt-in `--view summary` mode to `provider-replay config-check`.
- Keep the existing detailed config payload as the default and preserve current `config-check` behavior.
- Include a machine-readable `summary_view` that states the command is configuration-only, did not start serving, did not request probes, and does not provide daemon lifecycle management.
- Update E-06 in `FUNCTION_TREE.md` as a partial implementation with evidence and boundaries.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: add an opt-in config-check summary view for replay fake-provider configuration validation.

## Impact

- CLI parser and provider-replay dispatch in `tdxquant/cli.py`.
- Provider replay CLI tests in `tests/test_api_cli.py`.
- OpenSpec capability spec for `tdx-provider-transport-replay-service`.
- `FUNCTION_TREE.md` E-06 evidence and boundary text.
