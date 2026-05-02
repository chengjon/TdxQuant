## Why

当前仓库已经验证了通达信桌面端的 Win32/UIA/HID 交易链路原型，但还没有形成一条完整、稳定的“WSL 策略侧 <-> Windows 桌面 TDX”交互通路。与此同时，`/mnt/wd_mycode/tdxquant/tdx-docs` 展示出的官方 TdxQuant 能力远不止桌面自动化，还包括行情、板块、财务、公式计算和自选股操作，因此需要把这条分支收敛为一个明确的 Windows bridge 方案，而不是继续堆零散脚本。

## What Changes

- 新增一条专门面向通达信的 Windows bridge 方案，明确 WSL 调用侧、Windows sidecar 和 TDX 客户端之间的边界。
- 新增 TdxQuant 数据接口桥接能力，优先覆盖快照、K 线、标的信息、板块列表等非 GUI 数据能力。
- 新增 TdxQuant 公式桥接能力，覆盖指标公式、条件选股、专家公式及其批量处理入口。
- 新增通达信交易自动化桥接能力，保留现有 Win32/UIA 探测链路，并通过 HID 硬件键盘模拟补齐证券代码输入。
- 定义统一的结构化 JSON 返回格式、错误码和健康检查语义，供 WSL 侧脚本稳定调用。
- 为后续自选股管理、卖出、撤单、成交回读和事件推送预留扩展点，但本次不要求全部实现。

## Capabilities

### New Capabilities
- `tdx-windows-bridge`: 定义 Windows sidecar 的进程发现、健康检查、统一命令入口和 WSL 调用边界。
- `tdx-data-api-bridge`: 暴露通达信 TdxQuant 的非 GUI 数据能力，包括快照、K 线、标的信息和板块信息。
- `tdx-formula-bridge`: 暴露通达信公式系统能力，包括指标、选股、专家公式及批量计算。
- `tdx-trading-hid-bridge`: 暴露通达信交易自动化能力，结合 Win32/UIA 探测和 HID 键盘输入完成买入链路验证。

### Modified Capabilities

- None.

## Impact

- 新增一条独立 OpenSpec 变更，避免继续把通达信目标混在平安证券 Win32 变更里。
- 预计影响 `tdxquant` Python 包结构、CLI 命令、Windows 专用依赖和后续 sidecar 进程设计。
- 预计新增或扩展与 `pywin32`、`pyserial`、TdxQuant Python 接口相关的桥接模块。
- 预计新增 WSL 到 Windows 的调用约定，可能采用本地命令、文件交换、HTTP 或 IPC 中的一种。
- 需要在真实 Windows 桌面环境中验证 TdxQuant 官方接口可用性、通达信前台状态和 HID 硬件行为。
