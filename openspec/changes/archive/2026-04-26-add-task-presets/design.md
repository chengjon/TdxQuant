## Context

当前 `task` 层已经提供稳定 workflow，但适合日常操作的命令仍然较长，尤其是：

- `task trade-buy`
- `task trade-submit-once`
- `task guarded-trade-buy`

其中很多参数其实是环境级或策略级固定值，只需要在少数场合临时覆盖。`task profile` 更偏 workflow 默认行为，不适合承载“命令级快捷模板”，因此需要新增一层 `task preset`。

## Goals / Non-Goals

**Goals:**

- 提供 `task` 级别的可命名 preset。
- 允许查看当前可用 task preset 列表。
- 允许通过 preset 执行稳定 task workflow。
- 保证显式 CLI 参数优先于 preset 默认值。

**Non-Goals:**

- 不重写 `TdxTaskManager`。
- 不覆盖全部 task 子命令。
- 不与 `report` preset 合并成一个总配置。
- 不移除现有 `task` 原生命令。

## Decisions

### 1. task preset 与 task profile 分层

`task profile` 继续负责 workflow 内部默认值；`task preset` 负责命令级默认值，例如：

- `port`
- `refresh_before_trade`
- `required_block_code`
- `max_snapshot_price`
- 导出路径

这样可以把“稳定流程模板”和“底层 workflow 默认行为”分开管理。

### 2. 新增 `task presets` 与 `task run --preset ...`

采用与 `report` / `trade` 一致的发现方式：

- `task presets`
- `task run --preset <name>`

这样用户可以先查看模板，再调用模板，不需要记忆隐藏 alias。

### 3. 第一轮只覆盖高价值稳定 workflow

本次只支持：

- `refresh-environment`
- `trade-buy`
- `trade-submit-once`
- `guarded-trade-buy`

这些 workflow 的参数面虽然较宽，但大多是标量字段，适合 preset 合成。像 `watchlist-overview` 这类 `--code` 多值列表型命令暂不纳入。

### 4. `task run` 使用独立参数面与最终兜底默认值

为了让 preset 能真正覆盖命令级默认值，`task run` 会先解析成“多数参数默认 `None`”的 namespace，再按顺序合成：

1. preset 默认值
2. CLI 显式参数
3. 最终兜底默认值

这样不会被原生命令的 `argparse` 默认值提前占满。

## Risks / Trade-offs

- [覆盖范围有限] → 第一轮先覆盖最高价值 workflow，后续按需要扩展。
- [配置概念增多] → 文档明确区分 `task profile` 与 `task preset`。
- [task run 参数面仍然较宽] → 只作为 preset 执行入口，不替代原生短命令。
