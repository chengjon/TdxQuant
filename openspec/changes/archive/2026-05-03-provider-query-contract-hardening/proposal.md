## Why

`formula / runtime / block` 已经完成 provider-ready contract 收口，但 `market / meta / financial / transaction` 这四条查询主线仍缺少统一的查询元数据、fixture 覆盖和 discovery 标注。现在需要把现有查询入口整理成稳定 machine-readable contract，避免上层系统继续按各自特例消费。

## What Changes

- 新增统一查询 contract capability，定义 `market / meta / financial / transaction` 查询结果的 `data.query_meta` 共性元数据、稳定 `query_kind` 注册表，以及 capability-specific selector 的保留规则。
- 为现有 manager 和 CLI 查询入口补齐稳定查询元数据，不新增新命令或新 API 形态。
- 为查询主线补齐 representative replay fixtures，包括 success / empty-result / failure 样本。
- 收紧 capability discovery metadata，使查询能力显式暴露 `query_metadata.query_shapes`、字段筛选支持和 replay 支持。

## Capabilities

### New Capabilities
- `tdx-provider-query-contract`: 定义查询主线的共性 provider contract，包括 `data.query_meta`、稳定 `query_kind`、`requested_fields/returned_fields` 语义，以及 domain-native rows 的保留规则。

### Modified Capabilities
- `tdx-api-management`: manager 层查询入口需要稳定附加查询元数据，并在 replay mode 下保持一致 contract。
- `tdx-api-cli-entry`: CLI 查询入口需要输出与 manager 一致的查询 contract，并对 replay/flat/nested 命令保持一致语义。
- `tdx-provider-replay-fixtures`: replay fixture bundle 需要覆盖 `market / meta / financial / transaction` 查询能力的 representative 合约样本。
- `tdx-provider-capability-discovery`: capability discovery 需要为查询能力补充稳定的 query metadata 描述。

## Impact

- Affected code:
  - `tdxquant/api/bridge.py`
  - `tdxquant/api/manager.py`
  - `tdxquant/api/market.py`
  - `tdxquant/api/meta.py`
  - `tdxquant/api/financial.py`
  - `tdxquant/api/transaction.py`
  - `tdxquant/cli.py`
  - `tdxquant/replay_provider.py`
  - `tdxquant/replay_fixtures.py`
  - `tdxquant/provider_discovery.py`
- Affected APIs:
  - existing manager query methods
  - existing nested `api` commands
  - existing flat query commands
- Contract style:
  - additive / non-breaking hardening
  - top-level provider envelope unchanged
  - query metadata consolidated under `data.query_meta`
- No new external dependency and no new transport are introduced in this change.
