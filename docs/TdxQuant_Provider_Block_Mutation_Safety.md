# TdxQuant Provider Block Mutation Safety Contract

本文定义 TdxQuant 当前 `block` 写能力的 provider-facing 安全 contract。

适用范围：

- `TdxApiManager.block.create_sector(...)`
- `TdxApiManager.block.delete_sector(...)`
- `TdxApiManager.block.rename_sector(...)`
- `TdxApiManager.block.clear_sector(...)`
- `TdxApiManager.block.send_user_block(...)`
- `tdxquant api create-sector / delete-sector / rename-sector / clear-sector / send-user-block`
- `tdxquant tdx-create-sector / tdx-delete-sector / tdx-rename-sector / tdx-clear-sector / tdx-send-user-block`

不适用：

- `block.user_sectors(...)`
- `subscription-watch` 或其他长时事件流
- 桌面交易输出协议

## 1. Contract Goals

`block` 写能力会改变 TongDaXin 客户端本地状态，因此返回结果不能只停留在普通 `success / code / message`。

当前第一版 block mutation safety contract 解决 4 件事：

- 返回稳定的 `data.block_mutation` 摘要
- 为每次写尝试落本地 JSON 审计文件
- 在结果中暴露 audit artifact
- 保留可选 `mutation_key` 作为跨系统关联键

## 2. Canonical Payload Additions

在 provider result envelope 的 `data` 中，当前会新增：

```json
{
  "block_mutation": {
    "schema_version": "2026-04-28",
    "mutation_id": "7cdb0d7f7a4b47fcbb1a60871bb0f6a0",
    "mutation_key": "watchlist-sync-20260428-01",
    "operation": "send_user_block",
    "status": "applied",
    "block_code": "ZXG",
    "requested_stocks": ["000001.SZ", "600519.SH"],
    "requested_stock_count": 2,
    "show": true
  },
  "artifacts": {
    "audit_log_path": "runtime/block-mutations/20260428T120001123456Z-send_user_block-ZXG-7cdb0d7f.json"
  }
}
```

同时，top-level `artifacts` 也会暴露 provider-style artifact descriptor：

```json
[
  {
    "kind": "block_mutation_audit",
    "path": "runtime/block-mutations/20260428T120001123456Z-send_user_block-ZXG-7cdb0d7f.json"
  }
]
```

## 3. Field Rules

### `data.block_mutation`

稳定字段包括：

- `schema_version`
- `mutation_id`
- `mutation_key`
- `operation`
- `status`
- `block_code`

按动作条件出现的字段包括：

- `block_name`
- `requested_stocks`
- `requested_stock_count`
- `show`

当前 `status` 取值：

- `applied`
- `failed`

### `mutation_key`

`mutation_key` 是**调用方提供的关联键**，当前保证：

- 写入结果摘要
- 写入审计文件
- 可用于上层台账或重试关联

当前**不保证**：

- 自动 compare-and-skip
- 自动重复写拦截
- 强幂等执行语义

## 4. Audit Artifact

每次支持的 `block` 写动作，都会写一份本地 JSON 审计文件，包括失败尝试。

审计文件至少包含：

- `schema_version`
- `recorded_at`
- `mutation_id`
- `mutation_key`
- `operation`
- `status`
- `request`
- `result`

其中 `result` 保存的是本次底层调用返回的结构化结果快照。

## 5. Current Limits

当前第一版 contract 还没有做这些增强：

- 覆盖写 / 增量写的显式策略枚举
- 基于 `mutation_key` 的自动 skip
- 预读客户端状态后的重复写保护
- block sync task / daemon

这些属于下一阶段治理增强，不属于本包范围。
