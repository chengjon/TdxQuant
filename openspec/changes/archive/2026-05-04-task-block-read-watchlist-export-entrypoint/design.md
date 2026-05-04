## Context

`block.read_watchlist_snapshot` 已经作为 provider-level canonical read contract 落地，覆盖：

- 单个 `block_code`
- 保留原始板块顺序的标准化 `symbols`
- 空板块成功返回空 snapshot
- 不存在板块与非法成员的稳定失败语义

同时，导出型 task 代码实现已经存在：

- `TdxTaskManager.block_read_watchlist_export(...)`
- `tdxquant task block-read-watchlist-export ...`

当前需要补的是 contract formalization，而不是继续扩导出功能。

## Goals / Non-Goals

**Goals**

- 把 `task block-read-watchlist-export` 正式定义为稳定 task workflow。
- 明确 task 层先读取 provider-level `data.snapshot`，再执行单文件 JSON 导出。
- 明确 task 返回保留 `data.snapshot`，并附加薄的 `data.export` 与标准 task metadata。
- 明确 CLI `task block-read-watchlist-export` 的显式参数 contract。

**Non-Goals**

- 不新增 block read provider capability。
- 不增加 CSV / JSONL / Excel 导出。
- 不增加 flat CLI、preset、catalog entry、bundle 或 report。
- 不增加 task-only replay fixture。

## Decisions

### 1. `task block-read-watchlist-export` 是导出型薄包装，不是新的 provider contract

`task block-read-watchlist-export` 的职责是把稳定 provider-level snapshot 读取能力变成日常导出入口，而不是在 task 层重新设计一套 block read schema。

因此：

- task 输入直接映射到 `manager.block.read_watchlist_snapshot(...)`
- task 返回直接保留底层 `success/code/message/data.snapshot/artifacts/warnings`
- task 只追加：
  - `data.export`
  - 标准 task metadata / task profile / timing metadata

### 2. Task 输入只接受 `block_code`、显式输出路径和可选覆盖开关

第一版支持：

- `block_code`
- `output`
- `overwrite`

不支持：

- 自动目录命名
- 文件导入
- 多格式导出
- 多板块批量导出

这样这条 change 只解决“读取稳定 snapshot 并安全写出单文件 JSON”。

### 3. 导出内容只写 `data.snapshot`

导出文件内容固定为 provider-level `data.snapshot`。

不写：

- 整个 provider envelope
- task metadata
- report wrapper

这样导出文件可直接作为上层 watchlist snapshot 消费，而不把 task 层元数据混进去。

### 4. 默认拒绝覆盖，只有显式 `overwrite` 才允许替换已有文件

实现语义固定为：

- `overwrite=false`
  - 目标文件已存在时稳定失败
  - publish 过程中如果目标文件被并发创建，也必须稳定失败为 existing-file conflict
- `overwrite=true`
  - 允许替换已有目标文件

### 5. 写失败保留 snapshot，不留下成功态 export 元数据

如果 snapshot 读取成功，但路径校验或写文件失败：

- 顶层结果必须失败
- `data.snapshot` 继续保留
- `data.export` 只保留失败上下文，例如：
  - `output_path`
  - `error`

不写成功态：

- `overwritten`
- `file_size`

## Risks / Trade-offs

- [Task 层把读侧和导出副作用混成新 schema] → 通过要求 task 保留 `data.snapshot`、仅追加薄 `data.export` 来规避。
- [默认覆盖文件] → 通过默认拒绝覆盖并锁定 `overwrite` 语义来规避。
- [并发 publish 静默覆盖目标文件] → 通过要求 `overwrite=false` 使用 no-clobber publish 语义来规避。
- [导出失败被误判为成功] → 通过要求始终以顶层 `success` 判定导出是否完成来规避。

## Migration Plan

1. 将 `task block-read-watchlist-export` 作为独立 change 正式纳入 OpenSpec lifecycle。
2. 在 `tdx-task-management` 主 spec 中增加稳定 workflow requirement。
3. 保持现有实现与 focused tests 不变，仅同步 lifecycle 与主 spec。
4. 归档 change。

## Open Questions

- 无。第一版范围已经固定为单文件 JSON 导出 task。
