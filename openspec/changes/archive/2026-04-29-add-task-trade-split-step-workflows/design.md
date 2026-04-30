## Context

桌面交易主线已经完成稳定分步边界：`submit_ready(...)` 负责把当前买入请求推进到确认框边界，`confirm_current(...)` 负责推进当前确认框并处理结果窗。这两个 workflow 现在只存在于 trade manager / `trade` CLI 层，而日常批量调用、固定 preset 和上层项目复用更多依赖 `TdxTaskManager` 与 `task run --preset ...`。

这一包只需要把已经稳定的 trade workflow 上收为 task workflow，不重新设计交易语义。关键约束是：
- 继续让 trade manager 持有真正的桌面副作用、artifact 和 `trade_safety` 语义；
- task 层只做薄封装和日常入口整理；
- preset 解析必须保持显式 CLI 参数优先。

## Goals / Non-Goals

**Goals:**
- 新增 `TdxTaskManager.trade_submit_ready(...)`，支持可选 `refresh_before_trade`，并把调用透传给稳定 `submit_ready(...)`。
- 新增 `TdxTaskManager.trade_confirm_current(...)`，把当前确认边界推进包装成稳定 task workflow。
- 新增 `task trade-submit-ready` 和 `task trade-confirm-current`。
- 让 `task run --preset ...` 可以指向这两个新 workflow，并保留 CLI override 优先级。
- 给新 workflow 增加默认 task profile，避免上层每次都拼完整参数面。

**Non-Goals:**
- 不引入新的交易副作用或新的桌面自动化逻辑。
- 不重做 submission ledger、result dialog 规则或 confirmed-trade artifact 规则。
- 不把 split-step workflow 提升到 catalog / report 层。

## Decisions

### 1. Task workflow 继续作为 trade manager 的薄包装

`trade_submit_ready(...)` 和 `trade_confirm_current(...)` 都会沿用现有 task trade workflow 的返回结构：
- `input`
- 可选 `refresh_result`
- `trade_result`
- `artifacts`
- `result_dialog`
- task metadata

这样做的原因是上层不需要学习新的 task contract，同时底层 `trade_safety`、readiness summary 和 artifact 仍由 trade manager 决定。

备选方案是给 split-step task 单独设计一套结果 schema，但这会把同一条交易线拆成两套 contract，收益很低。

### 2. 只给 `trade_submit_ready` 暴露 refresh orchestration

`submit_ready` 仍然是“带请求参数”的 workflow，适合保留 `refresh_before_trade / refresh_market / refresh_force`。`confirm_current` 只是推进当前可见确认框，不再接受新下单参数，也不需要 task 层 refresh。

备选方案是统一让 `confirm_current` 也支持 refresh 参数，但这在行为上没有意义，还会让调用面更混乱。

### 3. Task preset 解析改成按命令判断最小必需参数

当前 `_build_task_preset_namespace(...)` 默认把除 `refresh-environment` 外的 task preset 都当成“完整下单请求”，强制要求 `port/code/price/quantity`。这不适用于 `trade-confirm-current`。

本包会把 required-argument 规则改成按 command 分流：
- `trade-buy / trade-submit-once / guarded-trade-buy / trade-submit-ready` 仍要求 `port/code/price/quantity`
- `trade-confirm-current` 不要求这些字段
- `refresh-environment` 继续无请求参数

这样改动最小，也能保证 preset 入口和直接 task 子命令行为一致。

### 4. 新增默认 task profile，而不是复用旧 profile 名

本包会新增：
- `trade_submit_ready`
- `trade_confirm_current`

到 `runtime/task-profiles.json` 和 `TASK_COMMAND_DEFAULT_PROFILES`。这样 preset / task 命令的 profile 选择保持清晰，不把分步边界混进现有 `trade_buy` 或 `trade_submit_once` 默认值。

## Risks / Trade-offs

- [Task 与 trade 入口再次漂移] → 保持 task 方法为薄透传，复用现有 trade argument 名称和返回结构。
- [Preset 规则变复杂] → 把 required-argument 判断限制在少量明确命令，不引入通用 DSL。
- [`confirm_current` 缺少 port/code 等输入后看起来不像传统 task] → 在 task input 中明确记录 boundary 参数和 requested action，保持可审计性。

## Migration Plan

1. 先补 RED 测试，覆盖 task manager、task CLI、task run preset 解析。
2. 实现 task manager 新 workflow，并接入 CLI / preset / profile。
3. 更新文档与 function map。
4. 运行 focused pytest、全量 `tests/`、compile 和 OpenSpec validate。

## Open Questions

- 后续是否需要把 `trade-submit-ready` / `trade-confirm-current` 进一步收口到 catalog entry；本包先不处理。
