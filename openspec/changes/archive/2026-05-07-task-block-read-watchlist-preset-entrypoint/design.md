## Context

`task block-read-watchlist` 已经作为稳定 task workflow 落地，覆盖：

- `TdxTaskManager.block_read_watchlist(...)`
- `tdxquant task block-read-watchlist ...`
- 成功结果保留 canonical `data.snapshot`

同时，项目已经有稳定的 task preset 体系：

- `runtime/task-presets.json`
- `task presets`
- `task run --preset ...`

当前需要补的是 formalization：把 `block-read-watchlist` 接进这套现有体系，而不是继续扩 preset 功能。

## Goals / Non-Goals

**Goals**

- 把 `block-read-watchlist` 正式定义为受支持的 task preset target。
- 明确 preset `options` 第一版只支持静态 `block_code`。
- 明确 `task run --preset ...` 仍然调度既有 `manager.block_read_watchlist(...)` workflow。
- 明确显式 CLI `--block-code` 对 preset 默认值的覆盖语义。
- 明确缺少 `block_code` 的 `block-read-watchlist` preset 在 preset execution 阶段稳定失败。

**Non-Goals**

- 不修改 preset schema。
- 不增加模板变量或路径插值。
- 不增加 catalog entry。
- 不增加新的 provider capability。
- 不增加导出、report、写回或后台控制语义。

## Decisions

### 1. 继续复用现有 task preset schema，不新增 preset 模型

第一版 preset 继续使用既有结构：

- `command`
- `description`
- `profile`
- `api_profile`
- `options`

`block-read-watchlist` 只是新增为一个允许的 `command`，而不是引入新的 preset schema。

### 2. preset `options` 只承载静态 `block_code`

当前 `task block-read-watchlist` 的独立 CLI 入口只要求：

- `block_code`

因此第一版 preset 默认值也只承载：

- `options.block_code`

不新增：

- `output`
- `export_output`
- `overwrite`
- 模板变量
- 写回参数

### 3. `task run` 继续使用通用 `--block-code` 覆盖 preset 默认值

为了让 preset 默认 `block_code` 可被显式 CLI 覆盖，同时不要求调用方绕回独立 task 命令，`task run` 路径继续接受：

- `--block-code`

这样：

- `task run --preset read-zxg-watchlist` 使用 preset 默认值
- `task run --preset read-zxg-watchlist --block-code MYZXG` 使用显式 CLI 覆盖值

### 4. 缺少 `block_code` 时在 preset execution 阶段早失败

`block-read-watchlist` preset 的最低必需字段是：

- `block_code`

如果 preset 缺少这个值，`task run --preset ...` 必须在 preset execution 阶段稳定失败，而不是把错误延后到更深层 workflow。

这条校验是第一版唯一一起补上的小幅 hardening；它不扩 preset schema，也不引入通用 extra-key validation。

### 5. representative preset 允许固定 `safe_read` API profile

这条 change 不扩 task-specific option surface，但 representative preset 可以和相邻 block read preset 保持一致，固定：

- `options.block_code`
- `api_profile = safe_read`

这属于代表性 preset 元数据对齐，不改变 task preset schema。

## Risks / Trade-offs

- [把这条线扩成第二套 preset 解析系统] → 通过复用现有 `_build_task_preset_namespace(...)` 和 `_handle_task_subcommand(...)` 来规避。
- [把 `block-read-watchlist` 误扩展成 catalog / report / export 入口] → 通过把 task-specific options 限定为 `block_code` 来规避。
- [配置错误被延后到更深层 dispatch] → 通过对缺少 `block_code` 的 preset 增加显式早失败来规避。

## Migration Plan

1. 将 `block-read-watchlist` 加入 task preset 允许命令集合。
2. 增加 representative preset 示例。
3. 在 `tdx-task-management` 主 spec 中增加 preset requirement。
4. 归档 change。

## Open Questions

- 无。第一版范围已经固定为静态 task preset 接入。
