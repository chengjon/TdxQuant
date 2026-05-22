## Why

`FUNCTION_TREE.md` E-13 already has a PingAn desktop extended broker capability probe and a direct `trade broker-capabilities` CLI path, but it is still marked partial because the probe is not discoverable through the stable preset/catalog planning surface. A registry reader can see the CLI evidence, but cannot yet verify the same boundary through catalog discovery without knowing the ad hoc command.

## What Changes

- Add a stable `broker-capabilities-default` trade preset for the PingAn desktop capability probe.
- Allow the trade preset runner to resolve and dispatch `broker-capabilities` without requiring buy/submit fields such as `port`, `code`, `price`, or `quantity`.
- Add a `broker-capabilities` command catalog entry for non-executing discovery and planning.
- Keep the probe diagnostic-only: no funds query, positions query, cancel request, broker-native push subscription, or default trade-flow integration.
- Update `FUNCTION_TREE.md` E-13 with the new preset/catalog evidence and explicit boundary.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-desktop-trading-extended-broker-capabilities`: the extended broker capability probe is available through a preset-backed `trade run` path without adding live broker side effects.
- `tdx-command-catalog`: the command catalog exposes a stable non-executing entry for the broker capability probe.

## Impact

- Affected code: `tdxquant/cli.py`, `tdxquant/trade/preset.py`.
- Affected runtime config: `runtime/trade-presets.json`, `runtime/command-catalog.json`.
- Affected tests: `tests/test_api_cli.py`.
- Affected registry/specs: `FUNCTION_TREE.md`, OpenSpec command catalog and desktop broker capability specs.
- No new external dependencies, migrations, account query execution, cancel execution, or broker-native push execution.
