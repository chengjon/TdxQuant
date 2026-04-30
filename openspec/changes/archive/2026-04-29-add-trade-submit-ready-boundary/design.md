## Context

当前稳定桌面交易线已经区分了：

- `trade health`：环境健康
- `trade preflight`：单次请求预检
- `trade dialog-readiness`：只读 dialog lookup readiness
- `trade buy` / `trade submit-once`：会自动推进确认的真实交易执行

但还没有一个稳定入口能把“已经发出提交动作并把确认框带出来”与“真正确认当前委托”分开。现有低层 `run_pingan_hid_submit_probe(...)` 已经能完成“填单 + HID submit”，因此最小方案不是重写买入主路径，而是把这条 pre-confirm 路径稳定化。

## Goals / Non-Goals

**Goals:**
- 暴露 `TdxTradeManager.pingan.submit_ready(...)` 作为稳定的 pre-confirm workflow。
- 暴露 `trade submit-ready` 作为稳定 CLI 入口。
- 在完成 submit probe 后，使用稳定 confirm lookup 规则验证当前确认框是否可见。
- 让结果明确表达“当前已经到达手动确认边界”。
- 给该 workflow 附带标准 trade metadata 和 safety metadata，并显式标记为 `local_state_mutating`。

**Non-Goals:**
- 不点击确认按钮。
- 不关闭结果窗。
- 不写 last-order state、order-event log 或 submission ledger。
- 不在这一包引入 task/preset 集成。
- 不在这一包设计“当前确认框自动推进”第二步 workflow。

## Decisions

### 1. 复用现有 HID submit probe 作为 pre-confirm side-effect path

`submit_ready(...)` 将复用 `run_pingan_hid_submit_probe(...)` 触发填单与 HID submit，而不是重写一条新的生产执行路径。这样范围最小，也不会改变现有 `buy` / `submit-once` 的稳定行为。

替代方案是从 `run_pingan_buy_fast(...)` 分叉出一个“到确认框前停止”的低层实现，但这会复制更多生产逻辑，风险更高，因此本包不采用。

### 2. submit probe 后再走稳定 confirm lookup 规则

workflow 在 probe 完成后，会复用稳定 trade manager 中已有的 `_find_confirm_target_for_lookup(...)` 规则验证确认框是否可见，并继续支持：

- `uia`
- `win32_experimental`

这样调用方看到的确认边界，与稳定 `buy` 线路使用的是同一套 dialog lookup 语义。

### 3. 结果保持 side-effecting，但不写 live-trade artifacts

`submit_ready(...)` 会改变本地 UI 状态，因此不能视为 read-only；但它又不会推进真实确认，因此不应写入“已成交/已委托”语义的 artifacts。结果将：

- 带标准 `trade_safety`
- 将 `side_effect_level` 标记为 `local_state_mutating`
- 不写 last-order state
- 不写 order event log
- 不写 submission ledger

这会要求 `attach_trade_safety_metadata(...)` 支持 workflow 级别的 side-effect override，而不是固定全局 `live_side_effecting`。

### 4. 将“手动确认要求”显式建模到结果中

workflow 成功时，不只返回“confirm dialog found”，还会在 `data.submit_ready` 中明确标出：

- 当前已经到达 pre-confirm boundary
- `manual_confirmation_required: true`

这样调用方无需从自由文本里猜当前状态。

## Risks / Trade-offs

- [submit probe 路径与生产 fast-buy 路径不完全同构] → 通过 probe 后再复用稳定 confirm lookup 规则，至少把 boundary 判定统一到稳定 lookup 语义。
- [调用方误把 submit-ready 当成已提交委托] → 结果显式标记 `manual_confirmation_required`，并保持 `local_state_mutating` 而非 `live_side_effecting`。
- [不写 artifacts 可能降低审计性] → 这是有意选择，用来避免把 pre-confirm workflow 误归类为真实交易结果；后续如果需要，可单独做 pre-confirm audit slice。

## Migration Plan

1. 先补 manager/CLI 测试。
2. 实现稳定 `submit_ready(...)` workflow。
3. 实现 `trade submit-ready` CLI 解析与分发。
4. 更新文档，将“二次确认边界”描述改为“已收口为 submit-ready 边界；如需完全自动分步，再考虑 confirm-current”。
