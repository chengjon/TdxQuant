## Context

当前项目已经把 TongDaXin 自定义板块生命周期和 `send_user_block(...)` 收口到 `block` 域，并提供了 manager 与 CLI 入口。但这些入口仍然把板块写操作当成普通同步调用处理：

- 成功时只有基础 `ok/code/message`
- 失败时没有标准 mutation summary
- 没有 durable audit artifact
- 调用方无法传入稳定关联键

这和上层项目对 `block` 的预期存在落差。`block` 不是纯查询能力，它会改变 TongDaXin 客户端状态，因此需要比普通查询更明确的治理边界。

## Goals / Non-Goals

**Goals:**

- 为 `create_sector / delete_sector / rename_sector / clear_sector / send_user_block` 定义稳定的 mutation summary。
- 为每次板块写操作落本地 JSON 审计文件，并在返回结果中暴露 artifact。
- 允许调用方传入可选 `mutation_key` 作为稳定关联键。
- 让 manager 和 CLI 共用同一套 block mutation contract。

**Non-Goals:**

- 不引入“先读取状态再自动跳过重复写”的强幂等逻辑。
- 不新增后台 daemon 或远程 provider transport。
- 不改变 `user_sectors` 这种只读动作。
- 不改造 TongDaXin 原始写能力的底层副作用模型。

## Decisions

### 1. 只对 block 写动作引入 mutation safety contract

本包只覆盖：

- `create_sector`
- `delete_sector`
- `rename_sector`
- `clear_sector`
- `send_user_block`

不覆盖 `user_sectors`。

理由：

- 这些动作都会改变客户端状态
- 读动作不需要审计和 mutation summary
- 保持 contract 语义清晰，避免把整个 `block` 域都误标成“有副作用”

### 2. 用 `mutation_key` 做关联，不承诺自动幂等跳过

调用方可以传入 `mutation_key`，系统会把它写入：

- `data.block_mutation`
- 审计文件
- provider artifact 关联信息

但本包不做“若同 key 已执行成功则自动跳过”的行为。

理由：

- 真正的幂等跳过需要定义比较基准和状态读取策略
- 现在先把跨系统关联键稳定下来，足以支撑审计、重试和上层台账
- 避免在没有充分验证的情况下引入误跳过

### 3. 审计文件在 bridge 层统一生成

板块写安全的共享逻辑放在独立 helper 中，并由 bridge block write wrappers 调用。这样：

- flat bridge CLI
- manager block domain

都会共享同一套 mutation summary 和审计产物逻辑。

理由：

- 不能只在 manager 层补，否则 flat bridge 路径会漂移
- 不能只在 CLI 层补，否则 Python 调用方得不到同样 contract

### 4. 返回 payload 同时暴露 capability-specific summary 和 artifact

每次 block 写结果都会新增稳定的 `data.block_mutation`，至少包含：

- `schema_version`
- `mutation_id`
- `mutation_key`
- `operation`
- `status`
- `block_code`
- `block_name`（如适用）
- `requested_stock_count`（如适用）
- `show`（如适用）

同时还会暴露：

- `data.artifacts.audit_log_path`
- provider top-level `artifacts` 中的 audit artifact descriptor

理由：

- `block_mutation` 是 capability-specific summary
- `data.artifacts` 方便现有本地调用方按 key 读取路径
- top-level `artifacts` 方便 provider-style 上层按统一 envelope 消费

### 5. 成功与失败都写审计文件

无论底层写动作成功还是失败，系统都写一份本地 JSON 审计文件。

理由：

- 失败路径同样需要排查依据
- 上层系统可以把 audit log 当成 durable attempt ledger
- 这比只记录成功更符合“可治理写操作”的目标

## Risks / Trade-offs

- [调用方可能把 `mutation_key` 误解成已实现强幂等] → 文档和 spec 明确只保证关联与记录，不保证自动跳过重复写。
- [本地 audit 文件会增加运行时文件数量] → 使用单独默认目录并允许调用方覆盖 `audit_dir`。
- [provider envelope 的 artifact 语义此前 mostly empty] → 本包只先为 block write 动作填充 artifact descriptor，不扩大其它能力范围。
- [bridge 层写文件会让单元测试更复杂] → 用共享 helper 和临时目录测试锁定行为。

## Migration Plan

1. 新增 provider block mutation safety spec。
2. 为 manager 和 CLI block write entrypoints 增加可选 mutation safety 参数。
3. 在 bridge 层接入共享 mutation summary 与审计文件 helper。
4. 补 focused tests，验证成功/失败都生成稳定 contract。
5. 更新文档并归档 change。

## Open Questions

- 后续是否需要基于 `mutation_key` 增加显式 replay/skip 语义，而不是只做关联键。
