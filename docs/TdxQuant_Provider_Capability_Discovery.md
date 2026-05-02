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

## 2. Capability Registry

`capabilities` 的 `data` 目前包含：

- `capabilities`
- `summary`
- `grading`

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
- `recommended_action`（如有）

当前 `severity` 固定字面值以实现为准，第一版至少使用：

- `info`
- `warning`
- `error`

## 5. 关键语义

`health` 和 `doctor` 的顶层 `success` 表示：

- 诊断命令本身是否成功产出结构化结果

它**不直接等价于**：

- 当前 provider 环境是否健康

也就是说，下面这种情况是允许的：

- top-level `success = true`
- `data.overall_status = "unavailable"`

这是刻意设计的，目的是让上层系统在环境不健康时，仍然能拿到完整的结构化诊断负载，而不是只拿到一个进程失败码。

## 6. 当前边界

这份 discovery contract 当前已经覆盖：

- capability registry
- provider health
- provider doctor
- capability grading

当前还没有覆盖：

- HTTP `capabilities / health / doctor` 服务化暴露
- `formula.screen` 的稳定业务 payload schema
- replay / fake discovery fixture

当前已单独文档化但不属于 discovery payload 本身的相关 contract：

- [TdxQuant_Provider_Subscription_Event_Contract.md](/opt/iflow/TdxQuant/docs/TdxQuant_Provider_Subscription_Event_Contract.md)
