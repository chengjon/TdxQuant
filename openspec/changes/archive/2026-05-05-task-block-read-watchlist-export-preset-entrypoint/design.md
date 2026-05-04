## Context

`task block-read-watchlist-export` 已经作为稳定 task workflow 落地，覆盖：

- `TdxTaskManager.block_read_watchlist_export(...)`
- `tdxquant task block-read-watchlist-export ...`
- 默认拒绝覆盖、显式 `--overwrite`、保留 `data.snapshot` 并追加薄 `data.export`

同时，项目已经有稳定的 task preset 体系：

- `runtime/task-presets.json`
- `task presets`
- `task run --preset ...`

当前需要补的是 formalization：把 `block-read-watchlist-export` 接进这套现有体系，而不是继续扩 preset 功能。

## Goals / Non-Goals

**Goals**

- 把 `block-read-watchlist-export` 正式定义为受支持的 task preset target。
- 明确 preset `options` 第一版只支持静态 `block_code`、`export_output`、`overwrite`。
- 明确 `task run --preset ...` 仍然调度既有 `manager.block_read_watchlist_export(...)` workflow。
- 明确显式 CLI 参数对 preset 默认值的覆盖语义。

**Non-Goals**

- 不修改 preset schema。
- 不增加模板变量或路径插值。
- 不增加 catalog entry。
- 不增加新的 provider capability 或 replay fixture。

## Decisions

### 1. 继续复用现有 task preset schema，不新增 preset 模型

第一版 preset 继续使用既有结构：

- `command`
- `description`
- `profile`
- `api_profile`
- `options`

`block-read-watchlist-export` 只是新增为一个允许的 `command`，而不是引入新的 preset schema。

### 2. preset `options` 使用 `export_output`，不是 `output`

当前 CLI 现实里：

- `task block-read-watchlist-export` 的导出目标参数 `dest` 是 `export_output`
- 通用 `task run --output` 已经用于“把整条命令 JSON 结果写到文件”

因此 preset 默认值必须写到：

- `options.block_code`
- `options.export_output`
- `options.overwrite`

而不是 `options.output`。

### 3. `task run` 需要单独的 `--export-output` 覆盖参数

为了让 preset 默认导出路径可被显式 CLI 覆盖，同时不污染现有 JSON-result `--output` 语义，`task run` 路径必须单独支持：

- `--export-output`

这样：

- `--output` 继续保留“整条命令结果写盘”语义
- `--export-output` 专门覆盖 `block-read-watchlist-export` preset 的导出目标文件

### 4. `overwrite` 必须保留 tri-state 语义

为了区分：

- preset 已提供 `overwrite=false`
- CLI 显式给 `--overwrite`
- CLI 显式给 `--no-overwrite`
- CLI 根本没有覆盖这个值

`task run` 的 `overwrite` 在 preset 路径下必须保留 tri-state 语义。实现上可采用：

- `BooleanOptionalAction`
- 默认值 `None`

### 5. 缺少 preset 必需字段时稳定失败

`block-read-watchlist-export` preset 的最低必需字段是：

- `block_code`
- `export_output`

如果 preset 缺少这些值，`task run --preset ...` 必须稳定失败，而不是隐式回退或把错误推迟到更深层 workflow。

## Risks / Trade-offs

- [`output` / `export_output` 混淆] → 通过显式分离两个参数语义规避。
- [覆盖开关无法区分 preset 默认值和 CLI 显式值] → 通过 tri-state `overwrite` 规避。
- [扩到模板变量/路径插值] → 明确保持静态 preset 范围，后续单独立项。

## Migration Plan

1. 将 `block-read-watchlist-export` 加入 task preset 允许命令集合。
2. 增加 representative preset 示例。
3. 在 `task run` 路径增加 `--export-output` 和 tri-state `overwrite` 覆盖语义。
4. 在 `tdx-task-management` 主 spec 中增加 preset requirement。
5. 归档 change。

## Open Questions

- 无。第一版范围已经固定为静态 task preset 接入。
