## Why

TdxQuant 已经有 `runtime.capabilities / runtime.health / runtime.doctor` 三个 discovery 入口，但当前 payload 仍然存在“已有字段未被正式锁定”和“部分高价值字段仍然偏人类可读、缺少 machine-readable 结构”的问题。同步 provider envelope 已经硬化完成，下一步最该做的就是把 discovery payload 本身收成可依赖的调用前探测 contract。

## What Changes

- Harden the `runtime.capabilities` payload so registry rows, summary counters, and grading metadata become explicitly stable and fixture-backed.
- Harden the `runtime.health` payload so probe context, checks, warnings, and recommended actions become fixed machine-readable structures instead of partially relying on free-form strings.
- Harden the `runtime.doctor` payload so findings use stable machine-readable identifiers and structured action linkage rather than remaining only human-readable advice.
- Keep the existing commands and entrypoints unchanged while upgrading replay fixtures and contract tests to lock the hardened discovery payload.
- Preserve compatibility-first behavior for existing human-readable warning lists while adding structured discovery action metadata instead of removing current fields immediately.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `tdx-provider-capability-discovery`: tighten the payload contract for `runtime.capabilities`, `runtime.health`, and `runtime.doctor`, including stable summary/grading metadata, structured recommended actions, and machine-readable finding identifiers.
- `tdx-provider-replay-fixtures`: require bundled discovery fixtures to cover the hardened capability registry, health, and doctor payload schemas as stable contract snapshots.

## Impact

- Affected code:
  - `tdxquant/provider_discovery.py`
  - `tdxquant/api/bridge.py`
  - `tdxquant/replay_fixtures.py`
  - `tdxquant/fixtures/provider/*.json`
- Affected APIs:
  - `TdxApiManager.runtime.capabilities()`
  - `TdxApiManager.runtime.health(...)`
  - `TdxApiManager.runtime.doctor(...)`
  - `tdxquant api capabilities|health|doctor`
  - `tdx-capabilities`, `tdx-health`, `tdx-doctor`
- Affected systems:
  - provider replay fixtures
  - discovery contract documentation
  - manager/CLI/fixture contract tests
