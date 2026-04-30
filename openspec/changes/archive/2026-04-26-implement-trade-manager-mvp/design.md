## Context

当前桌面交易能力已经有三层稳定资产：

1. 底层工具与执行层
   - `tdxquant/desktop/uia.py`
   - `tdxquant/desktop/win32.py`
   - `tdxquant/desktop/hid.py`

2. 券商适配与识别层
   - `tdxquant/brokers/pingan.py`

3. 现有稳定 CLI
   - `pingan-buy`
   - `pingan-buy-submit-once`

但顶层治理仍然散落在 `cli.py` 中，尤其是：

- 平安买入 profile 常量
- profile override 合并
- 合同号提取后的状态文件回填
- 控制台合同号输出
- 命令总耗时补充

这些行为已经不属于“命令解析”本身，而属于桌面交易 capability 的管理职责。

## Goals

- 引入 `TdxTradeManager` 作为桌面交易顶层管理入口。
- MVP 只覆盖平安买入稳定路径。
- 不重写 `desktop/uia.py` 真实执行逻辑，只在其外侧增加 manager 包装。
- 保持现有 CLI 参数和输出兼容。

## Non-Goals

- 本次不引入 `trade` 二级命令。
- 本次不抽象多券商统一下单接口。
- 本次不迁移所有桌面诊断命令。
- 本次不重构 Win32/UIA/HID 底层实现。

## Decisions

### 1. 新增 `tdxquant/trade/` 包

新增：

- `tdxquant/trade/context.py`
- `tdxquant/trade/manager.py`
- `tdxquant/trade/__init__.py`

其中：

- `context.py` 负责 trade profile、metadata、状态文件与事件日志写入等管理辅助逻辑
- `manager.py` 提供 `TdxTradeManager`

### 2. MVP 只提供平安 broker 代理

`TdxTradeManager` 先暴露：

- `manager.pingan.buy(...)`
- `manager.pingan.buy_submit_once(...)`

这样既能体现“交易 manager -> broker 代理”的结构，也避免过早抽象统一多券商接口。

### 3. Profile 从 CLI 常量迁移到 runtime 文件

新增 `runtime/trade-profiles.json`，承载：

- `stable`
- `balanced`
- `fast`
- `turbo`
- `submit_once`

CLI 中现有的平安买入 profile helper 将复用该文件，不再把配置常量硬编码在 `cli.py` 顶层。

### 4. 状态文件与事件日志由 manager 统一写入

MVP 中 `TradeManager` 每次平安买入调用后都执行：

- 写 `runtime/pingan-last-order.json`
- 追加 `runtime/pingan-order-events.jsonl`

CLI 保留合同号 stderr 输出，以维持现有使用习惯，但状态与日志回填不再由 CLI 直接负责。

### 5. CLI 保持兼容，只替换内部调用路径

现有：

- `pingan-buy`
- `pingan-buy-submit-once`

保留参数、命令名和输出结构；仅把内部执行切到 `TdxTradeManager`，并保留兼容 helper，避免测试和历史脚本断裂。

## Verification

- `TradeManager` 单元测试验证 profile 解析、manager metadata、状态文件与事件日志写入。
- CLI 分发测试验证 `pingan-buy` / `pingan-buy-submit-once` 使用 `TdxTradeManager`。
- 运行定向测试确保 API/task 相关入口不回归。
