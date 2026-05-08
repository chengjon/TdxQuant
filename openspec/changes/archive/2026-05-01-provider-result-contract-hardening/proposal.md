## Why

TdxQuant 已经有第一版 provider-facing 同步结果 envelope，但当前 manager、runtime discovery、CLI JSON 和 replay fixtures 之间仍然存在字段齐备性、兼容字段、退出码语义和文档口径不完全一致的问题。上层项目下一步更依赖稳定 machine contract，而不是继续扩查询原子能力，所以现在需要先把同步 provider contract 再硬化一版。

## What Changes

- Harden the canonical synchronous provider result envelope across manager-driven query, formula, and runtime discovery responses so every synchronous provider call returns the same stable top-level shape.
- Keep compatibility-first behavior by preserving the legacy top-level `ok` field as a temporary alias of `success` instead of removing it immediately.
- Tighten CLI JSON semantics so `tdxquant api ...` emits the same provider envelope on both success and failure while keeping non-zero exit codes for failed provider calls.
- Update provider replay fixtures so bundled snapshots cover the hardened envelope for success and failure query/formula responses plus `runtime.capabilities`, `runtime.health`, and `runtime.doctor`.
- Refresh the provider result and discovery documentation to describe the hardened envelope, compatibility period, and CLI semantics.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `tdx-provider-result-contract`: tighten the canonical synchronous envelope rules, compatibility alias behavior, container normalization, and CLI failure-envelope expectations.
- `tdx-provider-capability-discovery`: require `runtime.capabilities`, `runtime.health`, and `runtime.doctor` to fully conform to the hardened provider envelope and clarify diagnostic success semantics.
- `tdx-api-management`: require all manager-driven synchronous responses to flow through the hardened envelope builder with fixed metadata and compatibility fields.
- `tdx-api-cli-entry`: require CLI JSON entrypoints to reuse the hardened provider serializer and preserve stable JSON on non-zero exits.
- `tdx-provider-replay-fixtures`: require bundled replay fixtures to cover the hardened synchronous envelope and stable compatibility snapshots.

## Impact

- Affected code:
  - `tdxquant/api/context.py`
  - `tdxquant/api/manager.py`
  - `tdxquant/cli.py`
  - `tdxquant/provider_discovery.py`
  - provider replay fixture assets and loaders
- Affected APIs:
  - `TdxApiManager` synchronous query/formula/runtime responses
  - `tdxquant api ...` JSON output
  - runtime discovery JSON outputs and replay fixtures
- Dependencies and systems:
  - OpenSpec provider contract specs
  - provider contract docs
  - contract tests and fixture-based integration tests
