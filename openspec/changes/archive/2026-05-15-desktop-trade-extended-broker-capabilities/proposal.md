## Why

Desktop trading currently exposes guarded buy/sell/submit/confirm workflows, but the adjacent broker capabilities (funds, positions, cancel order, and broker-native push) are only implicit in adapter flags and can be mistaken for available runtime features. This change makes those capabilities discoverable as an explicit, read-only boundary so callers can see what is probeable, what is unsupported, and what would mutate broker state before any higher-level integration depends on it.

## What Changes

- Add a PingAn desktop extended broker capability probe that reports funds and positions as read-only capability probes without executing account queries.
- Classify cancel-order capability separately from read-only probes and mark its side-effect boundary as broker-state mutating.
- Add broker-native push feasibility output that records the current boundary instead of implying an event stream is available.
- Add CLI coverage for the probe under the desktop trade command surface.
- Add an independent risk document for the extended broker capability boundary.
- Update `FUNCTION_TREE.md` so the capability appears as a partially implemented, explicitly bounded feature node.

## Capabilities

### New Capabilities
- `tdx-desktop-trading-extended-broker-capabilities`: Covers read-only funds/positions probe metadata, cancel-order side-effect classification, broker-native push feasibility boundaries, and risk documentation for extended PingAn desktop broker capabilities.

### Modified Capabilities
- `tdx-desktop-trading-cli-entry`: Adds a non-executing CLI entry for the extended broker capability probe.

## Impact

- Affected code: `tdxquant/trade/*`, `tdxquant/trader/*`, `tdxquant/cli.py`, and focused trade/CLI tests.
- Affected docs/specs: OpenSpec specs, `FUNCTION_TREE.md`, and an independent risk document under `docs/`.
- No schema changes to existing query APIs, no live funds/positions data retrieval, no cancel execution, and no change to default upper-layer trading flow.
