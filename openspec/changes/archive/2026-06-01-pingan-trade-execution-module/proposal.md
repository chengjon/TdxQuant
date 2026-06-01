## Why

D-07 and D-08 are implemented, but PingAn order execution knowledge is still concentrated in `tdxquant/trade/manager.py`: request normalization, idempotency, safety gates, lifecycle owner checks, desktop adapter dispatch, result finalization, and audit projection sit in the same broad manager surface. The next mainline hardening step is to move that behavior behind a narrow internal execution seam while preserving every public `TdxTradeManager.pingan.*` caller contract.

## What Changes

- Add an internal PingAn trade execution module that models a normalized order execution request and dispatches it through a supplied desktop execution callback.
- Route at least the buy submit-once path through the new module as the tracer bullet for D-07/D-08 execution locality.
- Preserve existing public manager, CLI, task, catalog, audit, idempotency, max-price, lifecycle owner, and broker-readiness behavior.
- Add focused tests for the new module and compatibility tests for the delegated manager path.
- Update `FUNCTION_TREE.md` evidence and boundaries without changing D-07/D-08 status.

## Capabilities

### New Capabilities

### Modified Capabilities
- `tdx-desktop-trading-management`: Add an internal PingAn trade execution module seam for stable buy/sell/submit-once behavior while preserving public manager contracts.

## Impact

- Affected code: `tdxquant/trade/manager.py` and a new `tdxquant/trade/pingan_execution.py` internal module.
- Affected tests: new or existing focused trade manager/execution tests.
- Affected registry/specs: `FUNCTION_TREE.md`, `openspec/specs/tdx-desktop-trading-management/spec.md` after archive.
- No new public CLI syntax, no new catalog entries, no new desktop UIA/Win32 primitive, and no broad rewrite of PingAn lifecycle supervisor code in this slice.
