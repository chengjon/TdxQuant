## Context

`block.read_watchlist_snapshot` 已经作为 provider-level canonical read contract 落地，覆盖：

- 单个 `block_code`
- 保留原始板块顺序的标准化 `symbols`
- 空板块成功返回空 snapshot
- 不存在板块与非法成员的稳定失败语义

同时，`task block-read-watchlist` 的代码实现已经存在：

- `TdxTaskManager.block_read_watchlist(...)`
- `tdxquant task block-read-watchlist ...`

当前需要补的是 contract formalization，而不是继续扩功能。

## Goals / Non-Goals

**Goals**

- 把 `task block-read-watchlist` 正式定义为稳定 task workflow。
- 明确 task 层只做薄包装，不重定义 provider-level block read snapshot 结果结构。
- 明确 task 层附加的是 task metadata、task profile metadata 和 timing metadata。
- 明确 CLI `task block-read-watchlist` 的显式参数 contract。

**Non-Goals**

- 不新增 block read provider capability。
- 不增加文件导出、watchlist 导出、CSV/JSON 输出参数。
- 不增加 task preset、catalog entry、bundle 或 report。
- 不增加 task-only artifact 或 task-only summary schema。

## Decisions

### 1. `task block-read-watchlist` 是薄包装，不是第二套读取协议

`task block-read-watchlist` 的职责是把稳定 provider capability 变成日常 task 入口，而不是在 task 层重新设计一套 block read 协议。

因此：

- task 输入直接映射到 `manager.block.read_watchlist_snapshot(...)`
- task 返回直接沿用底层 `success/code/message/data.snapshot/artifacts/warnings`
- task 只追加标准 task metadata，而不是改写 `data.snapshot`

### 2. Task 输入只接受 `block_code`

第一版支持：

- `block_code`

不支持：

- 文件导出
- 目录扫描
- watchlist 文件自动发现
- 输出格式切换

这样这条 change 只解决“把 provider 级快照读取能力变成日常 task 入口”。

### 3. Task 层沿用标准 task metadata 附着模式

`TdxTaskManager.block_read_watchlist(...)` 应继续使用现有 task 模式：

- `_capture_task_timing(...)`
- `_attach_task_metadata(...)`

因此返回除了底层 provider envelope 外，还应保留：

- `data.task`
- `data.task_profile`
- `data.timing`

这让 `task block-read-watchlist` 在 task 层保持一致，但不污染底层 `data.snapshot` 结构。

### 4. CLI 只暴露显式 `--block-code`

CLI 层保持最薄：

- `task_subparsers.add_parser("block-read-watchlist")`
- `--block-code` 为必填
- 继续复用 `_add_task_common_arguments(...)`

这样 task CLI 只是日常入口，而不是新的导出/转换命令。

## Risks / Trade-offs

- [Task 层重复定义 block read snapshot result] → 通过要求 task 只追加 metadata、不改写 `data.snapshot` 来规避。
- [未来场景入口膨胀] → 明确不在本 change 中加入导出、preset、catalog、report。
- [CLI 参数膨胀] → 明确第一版只支持 `--block-code`。

## Migration Plan

1. 将 `task block-read-watchlist` 作为独立 change 正式纳入 OpenSpec lifecycle。
2. 在 `tdx-task-management` 主 spec 中增加稳定 workflow requirement。
3. 保持现有实现与测试不变，仅同步 lifecycle 与主 spec。
4. 归档 change。

## Open Questions

- 无。第一版范围已经固定为薄 task 包装。
