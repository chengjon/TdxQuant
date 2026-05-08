## Context

项目已经完成两件前置收口：一是 `TongDaXin` 交易线按范围关闭，二是 `add-securities-trader-gateway` 已把 `TradeService + PingAnDesktopTraderGateway` 和 canonical trader store 打出第一版骨架。当前剩余缺口不在“是否继续做标准化交易”，而在“是否把 `PingAN + HID` 变成可日常使用的真实交易主线”。

现状上，`PingAn` 买入快路径、卖出快路径和买入 `submit_once` 已存在，但卖出 `submit_once` 仍未实现；`trade` CLI 和 task/preset 也主要围绕买入和买入完整提交流程，导致主线路径不对称。现在这条 change 的目标，就是以最小范围把 `PingAN + HID` 收口成当前唯一的 live-trading mainline。

## Goals / Non-Goals

**Goals:**
- 明确 `PingAN + HID` 是当前项目唯一的真实交易执行主线。
- 补齐 `PingAn` 卖出 `submit_once` 链路，并保持 `buy/sell` 在快路径和完整提交路径上的对称性。
- 让 `TradeService + PingAnDesktopTraderGateway` 统一承接 `PingAn` live-trading 主线，并补齐 CLI/task/preset 的卖出入口。
- 保持现有 trade-audit、submission ledger、canonical trader store 继续工作，不打断现有买入命令和 split-step 入口。

**Non-Goals:**
- 不恢复 `TongDaXin` 真实交易，不把 `TongDaXin` 交易重新放回 live mainline。
- 不在本批次实现撤单、账户、持仓、委托页抓取或成交页同步。
- 不改变已有 trade-audit 聚合契约，不铺新的 broker 组合矩阵。

## Decisions

### 1. `PingAN + HID` 作为唯一 live-trading mainline，`TongDaXin` 保持关闭

设计上将把“真实交易执行”范围明确限定到 `PingAn` 桌面客户端加 HID 最终提交动作。`TongDaXin` 相关能力仅保留 bridge、探测和 HID baseline，不再承担真实交易闭环要求。

选择这样做，是因为 Windows 侧验收已经给出明确方向：项目能够在 `PingAn` 上完成窗口态识别、`submit_ready`、`confirm_current` 和 HID 提交，而 `TongDaXin` 交易环境既缺少权限，也不再是业务希望继续推进的主线。

备选方案：
- 继续保留 `TongDaXin` 为“恢复权限后再继续”的半活跃路径
  - 被否决，因为这会持续干扰当前交易主线的范围定义

### 2. 卖出完整提交按现有 `buy_submit_once` 结构补齐，不重做另一套流程模型

`sell_submit_once` 将沿用当前 `run_pingan_buy_submit_once` 的结构：
- UIA/Win32 写值仍用于代码/价格/数量输入
- HID 负责最终提交动作
- 确认按钮和结果窗仍走当前 `confirm_current` / result dialog 识别思路

差异只落在“先激活卖出页”“卖出方向控件定位”和“卖出方向结果/审计方法命名”上。这样可以最大化复用现有稳定积木，而不是再造一套与买入不同的 HID 提交流程。

备选方案：
- 把 `submit_once` 改成 side-neutral 的单函数并一次性重写买卖流程
  - 被否决，因为当前代码已存在稳定买入路径，重写风险高于补齐卖出分支

### 3. 主线收口继续通过 canonical trader 层，不把卖出能力直接散落到 task/CLI

`PingAnDesktopTraderGateway.place_order(...)` 目前对 `side=sell` 且 `execution_mode=submit_once` 直接抛 `NotImplementedError`。本批次会先补齐这一分支，再让：
- `trade sell`
- `trade sell-submit-once`
- `task trade-sell`
- `task trade-sell-submit-once`

优先走 `TradeService + PingAnDesktopTraderGateway`，而不是在 CLI/task 中直接复制 `trade_manager.pingan.*` 调用逻辑。这样可以保证 canonical order snapshot、trade fill、event store 和旧 `PingAn` 审计产物继续对齐。

备选方案：
- 先在 task/CLI 里直接调 `trade_manager.pingan.sell*`
  - 被否决，因为这会把新主线和兼容层再度分叉

### 4. 兼容命令继续保留，但新增明确的卖出稳定入口

现有 `trade buy` / `trade submit-once` 已被日常使用；本批次不会改掉它们的买入语义。新增对称入口时，将采用显式命名而不是修改旧命令含义：
- `trade sell`
- `trade sell-submit-once`
- `task trade-sell`
- `task trade-sell-submit-once`

同时补齐对应 `trade-presets` / `task-presets` 默认项，让卖出也能走与买入相同的 preset/default profile 机制。

备选方案：
- 给现有 `trade submit-once` / `task trade-submit-once` 增加 `--side`
  - 被否决，因为会改变现有命令的默认语义和脚本预期

## Risks / Trade-offs

- [卖出确认框与结果窗行为可能和买入略有差异] → 通过复用现有确认/结果窗探测逻辑并补充卖出专门测试，尽量把差异限制在 side 激活和文案层。
- [新旧命令并存会增加短期复杂度] → 保持“新增卖出入口，不改变现有买入入口”的策略，避免破坏当前脚本。
- [task/preset 扩展如果绕开 canonical trader 会重新分叉] → 要求新卖出入口统一委派到 `TradeService` 或对齐的 PingAn 主线适配层。
- [审计方法数增加会带来报表口径变化] → 不修改现有聚合逻辑，只要求新增卖出方法名沿用当前 method/status/broker 维度治理。

## Migration Plan

1. 在 `desktop/uia.py`、`trade/manager.py` 与 `trader/adapters/pingan_desktop.py` 补齐 `sell_submit_once`。
2. 扩展 `trade` CLI 的卖出稳定入口和 trade preset 默认项。
3. 扩展 task 层的卖出工作流、task CLI 命令和 task preset 默认项。
4. 用现有测试模式补齐 manager/gateway/CLI/task 覆盖，并更新功能图和使用文档。

回滚策略：
- 这次变更是增量补齐。若卖出 `submit_once` 或新卖出入口不稳定，可以关闭新增卖出命令和 preset，而不影响现有买入路径与 split-step 边界命令。

## Open Questions

- 无阻塞性开放问题；当前范围和方向已由 Windows 侧验收结论和项目决策确定。
