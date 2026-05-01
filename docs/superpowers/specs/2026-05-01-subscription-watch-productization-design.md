# Subscription Watch Productization Design

## Context

`subscription-watch` 已经具备基本的前台订阅运行能力，但当前输出仍偏向“命令执行结果”，还没有收口成一条稳定、可回放、可被上层集成消费的事件型 provider contract。

项目路线图已经明确两点：

- 查询与 discovery contract 需要优先稳定。
- `subscription` 是下一条高价值、适合整理成正式 provider contract 的能力线。

本设计将 `subscription-watch` 定义为一次前台运行的标准化 `run`，并把运行目录、事件文件、状态文件、总结文件和 replay fixture 一起稳定下来。

## Goals

- 把 `subscription-watch` 收口成前台长期运行命令的稳定文件契约。
- 固定独立 `run_id` 目录结构。
- 把 `events.jsonl` 定义为唯一 canonical 事件格式。
- 固定 `status.json`、`summary.json`、`manifest.json` 的结构和语义。
- 为 `subscription-watch` 补齐 representative replay fixtures、CLI tests 和文档。

## Non-Goals

- 不实现后台 daemon 化。
- 不实现 `start / stop / status / list` 命令。
- 不实现 HTTP streaming 或 provider service transport。
- 不把 `CSV` 提升为正式 contract；它只保留兼容导出角色。
- 不在本次设计中引入跨 run 聚合视图或持久 session 管理器。

## Recommended Approach

采用“契约优先的 run artifact 主线”。

核心思想是把一次 `subscription-watch` 执行视为一次标准化 `run`。上层调用方不再依赖终端输出推断运行状态，而是消费固定 run 目录里的 machine-readable artifacts。

与薄封装方案相比，这种方案能更稳地支撑 replay、contract test 和未来 fake provider。与直接预埋后台治理方案相比，它保持了 scope 克制，不会在前台稳定化阶段提前引入进程治理复杂度。

## Run Model

每次运行 `subscription-watch` 时，系统都必须生成一个新的 `run_id`，并在独立目录下写出本次运行 artifacts。

推荐目录形态：

```text
runtime/subscription-watch/<run_id>/
  manifest.json
  status.json
  summary.json
  events.jsonl
  events.csv         # optional compatibility export
```

说明：

- `events.jsonl` 是唯一 canonical 事件流。
- `status.json` 是运行中可刷新的快照。
- `summary.json` 是运行结束后的最终总结。
- `manifest.json` 描述本次 run 的 contract 元数据和输出路径。
- `events.csv` 如果存在，只能从 canonical JSONL 投影而来，不能拥有独立语义。

## Event Contract

`events.jsonl` 采用每行一个 JSON object 的方式记录事件。每个事件至少包含：

- `schema_version`
- `capability`
- `run_id`
- `provider_instance_id`
- `session_id`
- `subscription_id`
- `sequence`
- `event_type`
- `symbol`
- `source_ts`
- `event_ts`
- `reconnect_metadata`
- `payload`

约束：

- `sequence` 在单次 run 内必须单调递增。
- `event_ts` 必须始终存在，使用 RFC3339。
- `source_ts` 表示上游事件时间，若上游未提供可为 `null`。
- `event_type` 必须使用固定字面值，不允许自由文本漂移。
- `payload` 保留事件特有数据，但顶层公共字段必须稳定。
- `reconnect_metadata` 允许为空对象，但字段位置必须固定存在。

## Status And Finalization Contract

### status.json

`status.json` 表示运行中的最新状态快照，至少包含：

- `schema_version`
- `capability`
- `run_id`
- `state`
- `started_at`
- `updated_at`
- `session_id`
- `event_count`
- `last_sequence`
- `last_event_ts`
- `last_symbol`
- `output_paths`
- `warnings`

`state` 采用固定字面值：

- `starting`
- `running`
- `stopping`
- `completed`
- `failed`
- `interrupted`

### summary.json

`summary.json` 表示运行结束后的最终结果，至少包含：

- `schema_version`
- `capability`
- `run_id`
- `final_state`
- `started_at`
- `finished_at`
- `elapsed_ms`
- `event_count`
- `symbol_count`
- `session_id`
- `stop_reason`
- `warning_count`
- `artifacts`

`stop_reason` 采用固定字面值，例如：

- `completed`
- `keyboard_interrupt`
- `provider_disconnect`
- `provider_error`
- `write_error`

`status.json` 与 `summary.json` 的职责必须分离：前者服务运行中观测，后者服务结束后总结与 replay 对账。

## Manifest Contract

`manifest.json` 负责描述本次 run 的静态元数据，至少包含：

- `schema_version`
- `capability`
- `capability_version`
- `run_id`
- `created_at`
- `provider`
- `provider_mode`
- `requested_symbols`
- `output_dir`
- `artifacts`

其中 `artifacts` 应列出本次 run 预期生成的核心文件及相对路径，供 CLI 摘要、测试和后续 replay loader 统一消费。

## CLI Behavior

CLI 的正式主线是“文件可机读，终端可人读”。

因此：

- CLI 不承诺 stdout 事件流。
- CLI 可以输出启动摘要、进度提示和结束摘要。
- CLI 必须在结果中明确给出 `run_id`、输出目录和关键 artifact 路径。
- 机器消费统一走 `events.jsonl`、`status.json`、`summary.json`、`manifest.json`。

这能避免把人类友好的终端文案错误地升级成集成 contract。

## Fixtures And Testing

本次 change 必须同时补齐：

- representative `events.jsonl` fixture
- representative `status.json` fixture
- representative `summary.json` fixture
- replay fixture registry entries
- CLI tests
- 运行器或 manager 层 contract tests

测试应至少锁定：

- 独立 `run_id` 目录创建
- 固定 artifact 文件存在
- 事件字段完整性
- `sequence` 单调递增
- `status.json` 与 `summary.json` 字段稳定
- `Ctrl+C` 或中断结束时的 `final_state` / `stop_reason`

## Migration Strategy

本次设计采用“兼容新增”策略：

- 保留已有 `subscription-watch` 命令入口。
- 新增或调整其默认输出目录行为，使其落到标准 run 目录。
- 兼容已有 `CSV` 导出能力，但将其降级为投影产物。
- 现有终端文案可保留，但不能继续承诺为正式 machine contract。

## Risks

- 现有订阅回调事件结构如果过于松散，事件归一化层可能需要比预期更多的字段映射。
- 若当前运行器没有明确的中断/清理路径，`status.json` 和 `summary.json` 的最终一致性需要额外补强。
- 如果现有 fixture 只覆盖 happy path，本次需要补 degraded/interrupted 场景样例，否则 contract 锁定不足。

## Acceptance Criteria

设计落地后，至少满足以下条件：

1. 每次 `subscription-watch` 运行都会生成独立 `run_id` 目录。
2. `events.jsonl` 成为唯一 canonical 事件 contract。
3. `status.json`、`summary.json`、`manifest.json` 结构稳定且字段齐全。
4. CLI 文档与测试明确“文件主线、终端摘要”的输出边界。
5. replay fixtures 能提供稳定的 `subscription-watch` run artifacts 样例。
6. 对应 OpenSpec 变更、测试和文档全部校验通过。
