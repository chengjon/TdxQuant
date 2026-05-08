## Context

`block.sync_watchlist` 已经作为 provider-level canonical contract 落地，覆盖：

- `replace` / `merge`
- `create_if_missing`
- `dry_run`
- sync-level `mutation_key`
- governed `block_mutation` summary

同时，`task block-sync` 的代码实现已经存在：

- `TdxTaskManager.block_sync(...)`
- `tdxquant task block-sync ...`

但这条 task 场景入口尚未进入 OpenSpec lifecycle。当前需要补的是 contract formalization，而不是继续扩功能。

## Goals / Non-Goals

**Goals**

- 把 `task block-sync` 正式定义为稳定 task workflow。
- 明确 task 层只做薄包装，不重定义 provider-level `block sync` 结果结构。
- 明确 task 层附加的是 task metadata、task profile metadata 和 timing metadata。
- 明确 CLI `task block-sync` 的显式参数 contract。

**Non-Goals**

- 不新增 block sync provider capability。
- 不增加文件导入、watchlist 文件解析、CSV/JSON 导入。
- 不增加 task preset、catalog entry、bundle 或 report。
- 不增加 task-only artifact 或 task-only summary schema。

## Decisions

### 1. `task block-sync` 是薄包装，不是第二套同步协议

`task block-sync` 的职责是把稳定 provider capability 变成日常 task 入口，而不是在 task 层重新设计一套 block sync 协议。

因此：

- task 输入直接映射到 `manager.block.sync_watchlist(...)`
- task 返回直接沿用底层 `success/code/message/data.sync/data.block_mutation/artifacts`
- task 只追加标准 task metadata，而不是改写 `data.sync`

### 2. Task 输入使用 `symbols` 语义，CLI 仍通过 repeatable `--stock` 收集

为保持 task CLI 与既有用户习惯一致：

- CLI 继续使用 repeatable `--stock`
- task manager 内部转换为 `symbols`

第一版支持：

- `block_code`
- `stock[] -> symbols`
- `mode`
- `create_if_missing`
- `dry_run`
- `mutation_key`
- `show`
- `audit_dir`

不支持：

- 文件导入
- 目录扫描
- watchlist 文件自动发现

### 3. Task 层沿用标准 task metadata 附着模式

`TdxTaskManager.block_sync(...)` 应继续使用现有 task 模式：

- `_capture_task_timing(...)`
- `_attach_task_metadata(...)`

因此返回除了底层 provider envelope 外，还应保留：

- `data.task`
- `data.task_profile`
- `data.timing`

这让 `task block-sync` 在 task 层保持一致，但不污染底层 `data.sync` 结构。

### 4. `show` 默认保持与 provider-level block sync 一致

第一版 `task block-sync` 不单独偏离 provider-level 默认值。

因此：

- `show` 默认仍为 `true`

原因是：

- 与 `api block-sync`
- `tdx-block-sync`
- `manager.block.sync_watchlist(...)`

保持一致，避免 task 入口形成不同的桌面交互默认语义。

## Risks / Trade-offs

- [Task 层重复定义 block sync result] → 通过要求 task 只追加 metadata、不改写 `data.sync` 来规避。
- [未来场景入口膨胀] → 明确不在本 change 中加入 preset、catalog、report。
- [CLI 参数与内部 request 名称不一致] → 明确 `--stock -> symbols` 映射，并在 tests 中锁定。

## Migration Plan

1. 将 `task block-sync` 作为独立 change 正式纳入 OpenSpec lifecycle。
2. 在 `tdx-task-management` 主 spec 中增加稳定 workflow requirement。
3. 保持现有实现与测试不变，仅同步 lifecycle 与主 spec。
4. 归档 change。

## Open Questions

- 无。第一版范围已经固定为薄 task 包装。
