## Why

当前 `catalog run` 已经能统一执行 entry 和 bundle，但用户在真正执行前，仍然缺少一个稳定的“先看最终会跑什么”的入口。

这在交易和固定日常流程里都有风险：

- 不确定当前 CLI 显式参数是否真的覆盖了 preset / bundle step 默认值
- 不确定 bundle 局部执行最终会跑哪些 step
- 想做排障或文档化时，只能真的执行一次才能看到链路

需要新增一个纯解析、零副作用的 planning 能力。

## What Changes

- 在 `catalog` 下新增 `plan` 子命令。
- 支持对单条 entry 或 bundle 输出结构化执行计划，而不真正执行底层 workflow。
- 计划结果包含 source / preset / command / 关键合并参数以及 bundle 的选中 step 范围。
- 补充文档与测试。

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`: 增加零副作用 execution plan / preview 能力

### New Capabilities

None.

## Impact

- 影响 `tdxquant/cli.py`、catalog 相关 helper、CLI 测试与使用文档。
- 不修改 `TdxApiManager`、`TdxTaskManager`、`TdxTradeManager` 的业务行为。
- 不在 plan 模式中触发任何交易、报表或 task 执行。
