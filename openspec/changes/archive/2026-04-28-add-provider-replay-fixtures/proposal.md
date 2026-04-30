## Why

当前项目已经稳定了 `provider result`、`formula.screen`、`subscription event`、`capabilities/doctor` 和 `block mutation` 等关键 contract，但这些 contract 还缺少一组正式的内置 replay fixtures。没有稳定 fixture bundle，上层项目只能自己复制样例、手写 mock 或直接依赖 live Windows runtime，导致 contract test、离线联调和升级回归都很难收口。

## What Changes

- Introduce a built-in provider replay fixture bundle that covers the current high-value provider contracts.
- Add a shared loader/helper module so internal tests and external integrators can enumerate and load packaged replay fixtures in a stable way.
- Add focused contract tests that validate the packaged fixture bundle and prevent silent drift between fixture names, file formats, and expected payload shapes.
- Document the replay fixture catalog and narrow the scope to fixture distribution and loading, not a live fake transport or daemon.

## Capabilities

### New Capabilities
- `tdx-provider-replay-fixtures`: Stable built-in replay fixture bundle and loader contract for provider-facing JSON/JSONL capabilities.

### Modified Capabilities

## Impact

- Affected code:
  - new replay fixture helper module
  - new packaged JSON / JSONL fixture assets
- Affected tests:
  - fixture registry and loader tests
  - contract-oriented sample validation tests
- Affected docs:
  - provider replay fixtures documentation
  - roadmap / function map references
- Compatibility:
  - no live runtime or CLI entrypoint changes
  - existing provider contracts remain unchanged while gaining stable bundled samples for replay and contract testing
