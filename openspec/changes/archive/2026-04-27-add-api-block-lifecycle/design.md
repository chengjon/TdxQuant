## Context

当前项目已经明确把用户板块写动作从 `meta` 中独立到了 `block` 域，但这个域还只暴露了 `send_user_block(...)`。按官方接口文档，自定义板块相关能力实际上是一整组生命周期动作：

- 列表读取：`get_user_sector`
- 创建：`create_sector`
- 删除：`delete_sector`
- 重命名：`rename_sector`
- 清空成份股：`clear_sector`
- 添加成份股：`send_user_block`

如果这组能力不在 `block` 域中闭环，manager 边界会长期处于半成品状态：调用方能往板块里写股票，但不能稳定列出现有自定义板块，也不能创建、删除、清空或重命名。

## Goals / Non-Goals

**Goals:**

- 为 `block` 域补齐自定义板块生命周期闭环。
- 保持 `meta` 继续只承载只读公共元数据，而不是混入用户板块写能力。
- 为 nested `api` 暴露稳定日常入口，为 flat bridge CLI 暴露贴近官方函数名的入口。
- 复用现有 manager metadata / profile / timing 附加模式。

**Non-Goals:**

- 不新增 task/report/catalog 层的自定义板块场景封装。
- 不在本次做板块导入导出、批量事务化操作或额外状态文件治理。
- 不改 `send_user_block` 的既有行为。
- 不把自定义板块读能力挪回 `meta` 域。

## Decisions

### 1. 自定义板块整组能力都放进 `block` 子域

决策：

- `get_user_sector` 也归入 `block`，不放回 `meta`。
- `block` 域最终承载：
  - `user_sectors()`
  - `create_sector(...)`
  - `delete_sector(...)`
  - `rename_sector(...)`
  - `clear_sector(...)`
  - `send_user_block(...)`

原因：

- 虽然 `get_user_sector` 是读取动作，但它读取的是“用户自定义板块”这一生命周期对象，不是市场公共元数据。
- 这样可以把“用户板块资源”的完整边界保持在一个域里，后续如果再补更多板块管理能力，也不用再在 `meta/block` 间来回漂移。

### 2. nested `api` 用业务友好名，flat bridge 贴近官方函数名

决策：

- nested `api`：
  - `api user-sectors`
  - `api create-sector`
  - `api delete-sector`
  - `api rename-sector`
  - `api clear-sector`
- flat bridge：
  - `tdx-get-user-sector`
  - `tdx-create-sector`
  - `tdx-delete-sector`
  - `tdx-rename-sector`
  - `tdx-clear-sector`

原因：

- nested `api` 的使用目标是日常管理层，命名应与 `stock-list`、`sector-list`、`download-file` 保持一致。
- flat bridge 更接近官方接口函数名，便于与文档逐条映射和排查。

### 3. `clear_sector` 不复用 `send_user_block(..., stocks=[])`

决策：

- 如果运行时存在官方 `clear_sector`，则新增独立 bridge 包装并显式暴露。
- 不在 manager 层把 `clear_sector` 伪装成 `send_user_block(block_code, stocks=[])`。

原因：

- 官方接口文档已经把它定义为独立能力。
- 保持显式入口有利于覆盖矩阵、调用可读性和后续差异排查。
- 如果底层运行时未来对 `clear_sector` 和空列表 `send_user_block` 做出不同处理，当前抽象不会误导上层。

## Risks / Trade-offs

- [命令数量继续增长] → 这是当前项目明确接受的双入口策略，后续由 task/report/catalog 继续收口高频流程。
- [读能力放在 `block` 而非 `meta`] → 这是有意选择，用资源边界优先于“是否只读”来划域。
- [clear 语义与 send empty list 看似重复] → 通过显式独立入口保留语义清晰度，避免未来行为差异被隐藏。
