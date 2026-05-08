# 2026-05-07 Catalog Block Read Watchlist Entry Design

## Context

`block-read-watchlist` 已经作为稳定 task workflow 落地，并且已经接入现有 task preset 体系：

- `TdxTaskManager.block_read_watchlist(...)`
- `tdxquant task block-read-watchlist ...`
- `task run --preset read-zxg-watchlist`

同时，项目已经有稳定的 `catalog` 统一入口：

- `runtime/command-catalog.json`
- `catalog list`
- `catalog plan`
- `catalog run`

当前需要补的是 formalization：把 `read-zxg-watchlist` 接入这套现有 catalog 体系，而不是继续扩 catalog schema 或新增 catalog 子命令。

## Goals / Non-Goals

**Goals**

- 把 `read-zxg-watchlist` 正式定义为受支持的 preset-backed catalog entry。
- 明确 catalog entry 只作为现有 task preset 的可发现视图，不重复存储 `block_code` 默认值。
- 明确 `catalog list / plan / run` 都能消费这条 entry。
- 明确 `catalog plan` 能解析到 `task run --preset read-zxg-watchlist`，并展示解析后的 `block_code=ZXG`。
- 明确 `catalog run` 仍然委派到 preset-backed task path。

**Non-Goals**

- 不修改 catalog schema。
- 不新增 `catalog show`。
- 不支持 catalog 内联参数。
- 不新增 preset 编辑 / 删除 / create。
- 不引入新的 provider capability。
- 不引入 report / export / write-back / background control 语义。

## Decisions

### 1. 继续复用现有 command-catalog schema，不新增 catalog 模型

第一版 catalog entry 继续使用既有结构：

- `source`
- `preset`
- `description`
- `labels`

`read-zxg-watchlist` 只是新增为一个允许的 `task` source entry，而不是引入新的 catalog schema。

推荐新增的 catalog entry 形态如下：

```json
"read-zxg-watchlist": {
  "source": "task",
  "preset": "read-zxg-watchlist",
  "description": "统一入口下的 ZXG 板块标准化快照读取模板。",
  "labels": ["task", "block", "watchlist", "read"]
}
```

### 2. catalog entry 只承载 preset 视图，不重复存 `block_code`

`read-zxg-watchlist` 的默认值只存在于 `runtime/task-presets.json`。

catalog entry 只负责：

- 可发现
- 可计划
- 可执行

不负责重新定义 task preset 参数。

### 3. `catalog plan` 继续解析 preset-backed task path

`catalog plan --entry read-zxg-watchlist` 应当解析成：

- `task run --preset read-zxg-watchlist`

并展示至少以下已解析参数：

- `block_code=ZXG`

这样 catalog 的计划视图仍然是“预览真实将要执行的 preset-backed task”，而不是一套新的 catalog 参数系统。

### 4. `catalog run` 继续委派到 preset-backed task path

`catalog run --entry read-zxg-watchlist` 应当最终走：

- `task run --preset read-zxg-watchlist`

而不是直接改写为 `task block-read-watchlist ...` 或引入 catalog 自己的参数覆盖层。

## Risks / Trade-offs

- [把这条线扩成第二套 catalog 参数系统] → 通过只复用现有 `source/preset/description/labels` entry 结构来规避。
- [把 `read-zxg-watchlist` 误扩展成 report / export / write-back 入口] → 通过把 catalog entry 限定为 preset-backed 视图来规避。
- [catalog plan 与真实 preset 默认值漂移] → 通过让 `catalog plan` 继续解析现有 task preset defaults 来规避。

## Migration Plan

1. 在 `runtime/command-catalog.json` 新增 `read-zxg-watchlist` task source entry。
2. 增加 `catalog list / plan / run` focused tests，至少覆盖：
   - 默认 `catalog list` 包含 `read-zxg-watchlist`
   - `catalog list --entry read-zxg-watchlist`
   - `catalog plan --entry read-zxg-watchlist` 解析出 `block_code=ZXG`
   - `catalog run --entry read-zxg-watchlist` 仍委派到 `task run --preset read-zxg-watchlist`
3. 同步 `tdx-command-catalog` 主 spec，只补 entry 列表，不改 schema。
4. 归档 change。

## Open Questions

- 无。第一版范围已经固定为 preset-backed catalog entry 接入。
