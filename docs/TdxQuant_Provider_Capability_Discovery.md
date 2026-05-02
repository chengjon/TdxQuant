# TdxQuant Provider Capability Discovery

本文定义 TdxQuant 当前 provider-facing discovery contract。

它面向上层系统在真正调用 TongDaXin 能力前做 3 类动作：

- 列出当前 provider 暴露了哪些 capability
- 探测当前运行环境是否健康
- 获取结构化诊断建议，而不是只看自由文本

## 1. 当前入口

Manager:

- `TdxApiManager.runtime.capabilities()`
- `TdxApiManager.runtime.health(...)`
- `TdxApiManager.runtime.doctor(...)`

CLI:

- `api capabilities`
- `api health`
- `api doctor`
- `tdx-capabilities`
- `tdx-health`
- `tdx-doctor`

这些入口全部复用统一的 provider result envelope，顶层字段遵循：

- [TdxQuant_Provider_Result_Contract.md](/opt/iflow/TdxQuant/docs/TdxQuant_Provider_Result_Contract.md)

当前 discovery JSON 也必须满足这些公共约束：

- 顶层同时包含 `success` 和兼容别名 `ok`
- `warnings` 与 `artifacts` 始终是数组
- `data` 始终是对象

## 2. Capability Registry

`capabilities` 的 `data` 目前包含：

- `capabilities`
- `summary`
- `grading`

其中 `summary` 当前固定包含：

- `total`
- `by_domain`
- `by_stability`
- `by_side_effect_level`

其中 `grading` 当前固定包含：

- `stability_levels`
- `side_effect_levels`

单条 capability 当前固定字段：

- `name`
- `capability_version`
- `domain`
- `description`
- `stability`
- `side_effect_level`
- `entrypoints`
- `requires`

其中：

- `stability` 当前固定字面值：
  - `stable`
  - `beta`
  - `experimental`
- `side_effect_level` 当前固定字面值：
  - `read_only`
  - `local_state_mutating`
  - `live_side_effecting`

`entrypoints` 当前用于告诉上层从哪里调用，例如：

- `manager_method`
- `api_command`
- `flat_command`

## 3. Health Payload

`health` 的 `data` 当前固定包含：

- `overall_status`
- `context`
- `checks`
- `recommended_actions`
- `recommended_action_items`
- `warning_count`
- `warnings`

`overall_status` 当前固定字面值：

- `ok`
- `degraded`
- `unavailable`

`checks` 当前至少覆盖：

- `platform`
- `tqcenter_module`
- `query_runtime`
- `subscription_runtime`
- `desktop_window`
- `hid`

单条 check 当前固定字段：

- `status`
- `summary`
- `critical`
- `detail`（如有）
- `recommended_action`（如有）

`recommended_action_items` 是当前新增的 machine-readable action row，单条当前固定字段：

- `id`
- `summary`
- `severity`
- `related_checks`

其中：

- `id` 当前优先复用相关 check 名
- `summary` 是给人类显示的动作摘要
- `severity` 当前固定字面值以实现为准，至少包括 `info / warning / error`
- `related_checks` 是产生这条 action 的 check 名列表

兼容层说明：

- `recommended_actions` 仍然保留为字符串数组
- 它当前可视为 `recommended_action_items[*].summary` 的兼容投影

`status` 当前固定字面值：

- `ok`
- `warning`
- `failed`
- `unsupported`

## 4. Doctor Payload

`doctor` 在 `health` 的基础上额外提供：

- `findings`

单条 finding 当前固定字段：

- `id`
- `severity`
- `status`
- `summary`
- `critical`
- `related_checks`
- `recommended_action_id`
- `recommended_action`（如有）

其中：

- `id` 当前要求 machine-readable 且稳定，优先复用 check 名
- `related_checks` 标识这条 finding 对应的 check 列表
- `recommended_action_id` 如存在，应指向 `recommended_action_items[*].id`

当前 `severity` 固定字面值以实现为准，第一版至少使用：

- `info`
- `warning`
- `error`

## 5. 关键语义

`health` 和 `doctor` 的顶层 `success` 表示：

- 诊断命令本身是否成功产出结构化结果

当前顶层 `ok` 与 `success` 必须完全一致。

它**不直接等价于**：

- 当前 provider 环境是否健康

也就是说，下面这种情况是允许的：

- top-level `success = true`
- top-level `ok = true`
- `data.overall_status = "unavailable"`

这是刻意设计的，目的是让上层系统在环境不健康时，仍然能拿到完整的结构化诊断负载，而不是只拿到一个进程失败码。

对应 CLI 语义是：

- JSON 仍然输出完整 provider envelope
- 如果诊断命令本身成功产出结构化结果，CLI 返回 `0`
- 环境是否健康由 `data.overall_status`、`checks`、`findings`、`warnings` 判定，而不是由 CLI 文本错误替代

## 6. 当前边界

这份 discovery contract 当前已经覆盖：

- capability registry
- provider health
- provider doctor
- capability grading
- structured recommended action rows
- finding to action linkage

当前还没有覆盖：

- HTTP `capabilities / health / doctor` 服务化暴露
- `formula.screen` 的稳定业务 payload schema
- replay / fake discovery fixture

当前已单独文档化但不属于 discovery payload 本身的相关 contract：

- [TdxQuant_Provider_Subscription_Event_Contract.md](/opt/iflow/TdxQuant/docs/TdxQuant_Provider_Subscription_Event_Contract.md)
