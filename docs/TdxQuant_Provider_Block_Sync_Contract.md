# TdxQuant Provider Block Sync Contract

本文定义 TdxQuant 当前 `watchlist -> TongDaXin custom sector` 单向同步能力的 provider-facing contract。

适用范围：

- `TdxApiManager.block.sync_watchlist(...)`
- `tdxquant api block-sync ...`
- `tdxquant tdx-block-sync ...`

不适用：

- `block.user_sectors(...)`
- 双向 `TongDaXin block -> 上层 watchlist` 同步
- 文件导入式 watchlist 解析
- `task / report / catalog` 场景包装

## 1. Contract Goals

`block sync` 不是普通的单次板块写入，而是“同步意图 -> 当前状态探测 -> diff -> 治理决策 -> 真实写入或只返回计划”。

当前 contract 固定解决这些问题：

- 明确 `replace` / `merge` 两种同步语义
- 支持 `create_if_missing`
- 支持 `dry_run`
- 暴露稳定的 `data.sync` 结果摘要
- 对真实执行保留底层 `block_mutation` metadata
- 支持 sync-level `mutation_key` replay / conflict 规则
- 为 `applied / noop / rejected / failed / dry-run plan` 都写本地 sync audit artifact

## 2. Request Contract

当前稳定请求字段：

- `block_code`
- `symbols`
- `mode`
  - `replace` 默认
  - `merge`
- `create_if_missing`
  - 默认 `false`
- `dry_run`
  - 默认 `false`
- `show`
  - 默认 `true`
- `mutation_key`
  - 可选
- `audit_dir`
  - 可选

约束：

- `symbols` 按集合语义规范化：
  - 去重
  - 过滤空值
  - 统一代码格式
- `replace`
  - 目标成员集合最终等于 `symbols`
- `merge`
  - 目标成员集合最终等于 `observed ∪ symbols`

## 3. Result Contract

当前同步结果在 provider envelope 的 `data` 中固定暴露：

```json
{
  "sync": {
    "schema_version": "2026-05-03",
    "block_code": "ZXG",
    "mode": "replace",
    "create_if_missing": false,
    "dry_run": false,
    "show": true,
    "status": "applied",
    "governance_decision": "execute",
    "governance_reason": "state_diff_detected",
    "created_block": false,
    "would_create_block": false,
    "added_symbols": ["600519.SH"],
    "removed_symbols": [],
    "unchanged_symbols": ["000001.SZ"],
    "desired_symbols": ["000001.SZ", "600519.SH"],
    "observed_symbols": ["000001.SZ"]
  },
  "block_mutation": {
    "operation": "send_user_block",
    "status": "applied"
  },
  "artifacts": {
    "audit_log_path": "runtime/block-sync/20260503T100000000000Z-block-sync-ZXG-1234abcd.json"
  }
}
```

其中：

- `data.sync` 是同步视角主摘要
- `data.block_mutation` 是最后一个真实执行阶段的 governed write metadata
- `data.block_mutation_stages` 仅在 `create -> send` 多阶段执行时出现
- `data.artifacts.audit_log_path` 指向 block sync 自己的 audit artifact
- top-level `artifacts` 会包含：
  - `block_sync_audit`
  - 以及真实执行阶段暴露出来的 `block_mutation_audit`

## 4. Result Status Rules

当前 `data.sync.status` 稳定取值：

- `applied`
- `noop`
- `rejected`
- `failed`

对应语义：

- `applied`
  - 已执行真实写入，或 `dry_run` 返回了可执行计划
- `noop`
  - 当前状态已等于目标状态，或 `mutation_key` 命中同请求 replay
- `rejected`
  - 请求被治理层拒绝，例如缺少目标板块且 `create_if_missing=false`
- `failed`
  - 运行时 probe 或写入阶段失败

## 5. `mutation_key`

`mutation_key` 当前是 **sync-level request identity**，不是底层单次写入的 mutation identity。

当前保证：

- 同 `mutation_key` + 同 canonical sync request
  - 短路 replay
- 同 `mutation_key` + 不同 canonical sync request
  - 稳定拒绝

当前不要求：

- 把同一个 sync-level `mutation_key` 透传成底层 `create_sector` / `send_user_block` 的 mutation key

## 6. Replay Fixtures

当前内置 representative fixtures：

- `block-sync-replace-applied`
- `block-sync-merge-noop`
- `block-sync-replace-rejected`
- `block-sync-replace-plan`

默认 replay capability：

- `block.sync_watchlist`

可通过：

- `TdxApiManager(..., provider_mode="replay")`
- `tdxquant api block-sync --provider-mode replay`
- `tdxquant tdx-block-sync --provider-mode replay`

直接回放。

## 7. Current Limits

当前第一版仍然限制在：

- 单向 `watchlist -> TongDaXin block`
- 直接传入标准化 `symbols`
- 不做 watchlist 文件导入
- 不做双向同步
- 不做 task/preset/catalog 场景入口
