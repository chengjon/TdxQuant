## Why

TdxQuant 已经具备公式批量选股能力，但当前 `formula_process_mul_xg` / `formula-mul-xg` 的返回结构更接近底层原始结果，不适合直接作为上层项目长期依赖的正式 contract。现在需要新增一个稳定的 `formula.screen` provider contract，把“公式选股 -> 标准股票列表”收口成可版本治理、可做 contract test 的正式入口。

## What Changes

- Introduce a provider-facing `formula.screen` capability that wraps batch stock-picking formula execution into a stable machine-readable payload.
- Add a normalized formula screen payload schema with stable fields for input summary, matched symbols, unmatched symbols, per-symbol rows, and formula series details.
- Expose the new capability through `TdxApiManager.formula.screen(...)`, nested `api formula-screen`, and flat `tdx-formula-screen`.
- Keep existing raw formula entrypoints such as `formula-mul-xg` available for backward compatibility instead of repurposing their payload shape.
- Add contract-focused tests and documentation so upstream systems can safely consume the new stable screen payload.

## Capabilities

### New Capabilities
- `tdx-provider-formula-screen`: Stable provider-facing contract for batch stock-screen formula execution and normalized screen result payloads.

### Modified Capabilities
- `tdx-api-management`: Add a stable manager-visible `formula.screen(...)` action that returns normalized formula screening results without replacing the existing raw batch formula methods.
- `tdx-api-cli-entry`: Add nested `api formula-screen` and flat `tdx-formula-screen` commands for the new stable formula screen contract.

## Impact

- Affected code:
  - formula normalization helpers
  - `tdxquant/api/bridge.py`
  - `tdxquant/api/formula.py`
  - `tdxquant/api/manager.py`
  - `tdxquant/cli.py`
- Affected tests:
  - bridge formula normalization tests
  - manager formula contract tests
  - CLI parser/dispatch/provider envelope tests
- Affected docs:
  - provider formula contract documentation
  - roadmap references for `formula.screen`
- Compatibility:
  - existing `formula-xg` / `formula-mul-xg` entrypoints remain available
  - the stable contract is introduced as a new preferred capability rather than a breaking rewrite
