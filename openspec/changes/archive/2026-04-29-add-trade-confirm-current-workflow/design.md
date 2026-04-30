## Context

桌面交易线已经有：

- `trade health`
- `trade preflight`
- `trade submit-ready`
- `trade dialog-readiness`
- `trade buy` / `trade submit-once`

其中 `submit-ready` 已经把“提交到确认框可见”稳定化，但还没有与之对称的第二段 stable workflow。当前如果调用方已经让确认框出现，只想推进当前确认并处理结果窗，只能回到完整 buy flow 或低层实验命令。

## Goals / Non-Goals

**Goals:**
- 暴露 `TdxTradeManager.pingan.confirm_current(...)` 作为稳定第二段 workflow。
- 暴露 `trade confirm-current` CLI 入口。
- 复用稳定 confirm/result lookup 规则点击当前确认框。
- 在确认后识别当前结果窗，并支持可选自动关闭结果窗。
- 为已确认动作写标准 state/event artifacts，但不引入 submission-ledger 语义。

**Non-Goals:**
- 不重新填单。
- 不重新校验 `code/price/quantity` 风险门。
- 不在这一包把 split-step 流程上收到 task/preset。
- 不在这一包设计更细粒度的“仅关闭当前结果窗”独立 workflow。

## Decisions

### 1. confirm-current 只操作当前可见 confirm dialog

workflow 不接收交易请求字段，而是明确建模为“推进当前可见确认框”的动作。这样它与 `submit-ready` 形成清晰配对：

- `submit-ready`：把请求推进到确认边界
- `confirm-current`：推进当前确认边界

替代方案是再次要求调用方提供 `code/price/quantity`，但这会让接口语义混淆成“重做一遍下单请求”，因此不采用。

### 2. 结果窗检测失败按 degraded 处理，而不是直接失败

确认点击成功后，真实副作用已经发生。此时如果结果窗没有在预期时间内被识别，更适合视为“已确认，但后续可观察性不足”，而不是把整次 workflow 判成未执行。因此：

- confirm lookup / confirm click 失败 -> `failed`
- result dialog 未识别 -> `warning`
- result dialog 可选关闭失败 -> `warning`

### 3. 写 state/event artifacts，但不写 submission ledger

`confirm-current` 属于 live confirmed action，因此会写：

- last-order state
- append-only order event log

但它不持有 caller request fingerprint，也不应假装有 submission-key 幂等语义，因此不写 submission ledger。

### 4. 默认允许自动关闭结果窗

workflow 设计成 split-step 的第二段，默认 `close_result_dialog=True`。这样：

- `submit-ready`
- `confirm-current`

组合后可形成一个稳定分步全流程，并且在默认情况下最终恢复主界面。若调用方希望保留结果窗，可显式关闭该选项。

## Risks / Trade-offs

- [当前确认框可能不对应调用方主观预期的委托] → 明确接口语义是“当前确认框”，并要求调用方先用 `submit-ready` 或 `dialog-readiness` 建立边界感知。
- [结果窗未识别时，调用方可能不确定是否需要手动收尾] → 结果中给出 degraded/warning 和明确 next_action。
- [不写 submission ledger 会让 split-step workflow 缺少 keyed 幂等] → 这是有意边界，后续如果要支持 keyed split-step，需要独立设计跨两段 workflow 的 ledger model。

## Migration Plan

1. 先补 manager/CLI 测试。
2. 实现 stable `confirm_current(...)` workflow。
3. 实现 `trade confirm-current` CLI 解析与分发。
4. 更新文档，把“pre-confirm / confirm-current 分步边界”描述改成已完成。
