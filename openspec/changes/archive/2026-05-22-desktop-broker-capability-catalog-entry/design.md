## Context

The current extended broker capability probe is intentionally diagnostic. It reports boundary metadata for funds, positions, cancel order, and broker-native push support, and its CLI path does not execute those capabilities. Existing trade presets mainly target state-changing buy or submit workflows, so the generic `trade run --preset ...` path currently assumes trading fields are required.

## Goals / Non-Goals

**Goals:**

- Make the broker capability probe discoverable via runtime trade presets.
- Make the same probe discoverable and plannable via the command catalog.
- Preserve the read-only and classification-only boundaries already expressed by the probe payload.
- Keep `catalog plan` non-executing and keep `trade run --preset broker-capabilities-default` limited to the existing probe dispatch.

**Non-Goals:**

- Do not execute funds or positions extraction.
- Do not submit cancel requests.
- Do not open broker-native push subscriptions.
- Do not add query API integration or make the probe part of the default trade happy path.
- Do not generalize trade preset validation beyond the minimum command-specific required fields needed here.

## Decisions

- Add `broker-capabilities` to trade preset command defaults with the existing balanced desktop profile.
- Make `_build_trade_preset_namespace` use command-specific required fields: buy and submit flows keep their current required inputs, while broker capability probes require no buy/submit arguments.
- Store the preset in `runtime/trade-presets.json` with `broker: pingan_desktop` and no side-effecting options.
- Add a command catalog entry named `broker-capabilities` whose source is `trade` and preset is `broker-capabilities-default`.
- Verify both direct preset dispatch and catalog non-executing plan output.

## Risks / Trade-offs

- Adding a preset-backed diagnostic trade command expands the meaning of `trade run` beyond order-flow commands. The mitigation is command-specific validation and tests that preserve the probe-only boundary.
- The catalog entry may look executable because catalog entries can be run. The preset still dispatches only to the existing diagnostic probe, and `FUNCTION_TREE.md` must explicitly say it does not perform funds/positions/cancel/push actions.
