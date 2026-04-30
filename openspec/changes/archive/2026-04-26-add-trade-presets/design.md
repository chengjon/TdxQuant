## Context

当前交易侧已经具备：

- `TdxTradeManager`
- `trade buy`
- `trade submit-once`
- `trade profile`

但 `trade profile` 主要解决的是提交链路内部的延时和执行参数，不负责端口、窗口、输出路径等命令级默认值。对日常使用来说，还缺一层“固定环境参数 + 保留交易三要素动态输入”的快捷命令模板。

## Goals / Non-Goals

**Goals:**

- 提供 `trade` 级别的可命名 preset。
- 允许查看当前可用 preset 列表。
- 允许通过 preset 执行 `buy` 或 `submit-once`。
- 保证显式 CLI 参数优先于 preset 默认值。

**Non-Goals:**

- 不重写 `TdxTradeManager`。
- 不改变底层 `desktop/uia.py` 真实提交流程。
- 不移除既有 `trade` / `pingan-buy*` 命令。
- 不把 `task` / `report` preset 统一重构到一个总线里。

## Decisions

### 1. trade preset 与 trade profile 分层

`trade profile` 继续负责提交流程内部参数；`trade preset` 负责命令调用级默认值，例如：

- `port`
- `profile`
- `title_key`
- `max_depth`
- `dialog_timeout`

这样可以避免“一个配置文件同时承担内部策略和命令模板”。

### 2. 新增 `trade presets` 与 `trade run --preset ...`

采用与 `report` 相同的发现方式：

- `trade presets`
- `trade run --preset <name>`

这样用户可以先枚举可用模板，再选择执行，不需要记住隐藏别名。

### 3. `trade run` 使用独立参数面，默认值为空

为了让 preset 真正覆盖命令默认值，`trade run` 会使用一套独立的参数定义，其大部分字段默认值为 `None`。然后按顺序合成：

1. preset 默认值
2. CLI 显式参数
3. 最终兜底默认值

这样不会被 `argparse` 的静态默认值提前占满。

### 4. preset 只支持稳定交易命令

本次只允许 preset 目标命令为：

- `buy`
- `submit-once`

不把实验性诊断命令并入 preset 机制。

## Risks / Trade-offs

- [配置概念增多] → 通过文档明确区分 `profile` 与 `preset` 职责。
- [trade run 参数面较宽] → 只作为 preset 执行入口，不替代既有短命令。
- [用户误以为 preset 会固定标的参数] → 内置示例只固定环境参数，`code/price/quantity` 仍推荐调用时传入。
