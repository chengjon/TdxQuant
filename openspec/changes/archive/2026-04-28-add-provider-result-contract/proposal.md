## Why

TdxQuant 已经具备较完整的查询、公式和 manager/CLI 入口能力，但对上层系统而言，同步调用结果仍缺少稳定、统一、可版本治理的机器协议。现在需要先固定 provider-facing JSON result contract，才能让 `mystocks`、`quantix-rust` 和后续集成方安全编写 contract test、bridge 适配和长期兼容逻辑。

## What Changes

- Introduce a provider-facing synchronous JSON result contract for TdxQuant query and formula style capabilities.
- Define a stable result envelope with required fields for success/error semantics, capability identity, schema/version metadata, timing metadata, warnings, data payload, and artifacts.
- Standardize field formatting expectations for timestamps, symbols, enums, and CLI exit code behavior when JSON output is requested.
- **BREAKING** Align manager-driven query results with the new provider result envelope without collapsing existing domain boundaries.
- **BREAKING** Align nested `api` CLI output and flat bridge CLI JSON output with the same provider result envelope for machine consumption.
- Document scope boundaries so this package covers synchronous provider results only; subscription event streams, capability discovery, and desktop trade outputs remain out of scope for later changes.

## Capabilities

### New Capabilities
- `tdx-provider-result-contract`: Provider-facing synchronous JSON result envelope, field formatting rules, versioning fields, and failure semantics for machine-readable TdxQuant outputs.

### Modified Capabilities
- `tdx-api-management`: Manager-driven query and formula style results adopt the provider-facing result envelope and standardized metadata semantics.
- `tdx-api-cli-entry`: Nested `api` commands and flat bridge JSON outputs adopt the same provider-facing result envelope and CLI exit code expectations.

## Impact

- Affected code:
  - query/result serialization helpers
  - `tdxquant/api/manager.py`
  - `tdxquant/cli.py`
  - JSON output writers and related runtime helpers
- Affected tests:
  - CLI JSON output tests
  - manager result-shape tests
  - new contract-focused fixture tests
- Affected docs:
  - provider contract documentation
  - integration guidance for upstream systems
- Out of scope for this package:
  - capability discovery / health probe
  - subscription JSONL lifecycle contract
  - block mutation safety
  - desktop trading output normalization
