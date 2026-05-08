## Context

当前仓库已经有一套通达信桌面自动化原型：

- `tdxquant/cli.py`
- `tdxquant/win32_api.py`
- `tdxquant/uia_inspector.py`
- `tdxquant/hid_bridge.py`

这套原型已经证明两件事：

- 通达信桌面端可以被 Win32/UIA 探测、定位、读回和部分非物理触发。
- 交易代码输入是核心阻塞点，当前需要 HID 硬件键盘模拟来补齐。

另一方面，`/mnt/wd_mycode/tdxquant/tdx-docs/TdxQuant接口说明文档.md` 说明官方 TdxQuant Python 接口已经覆盖大量非 GUI 能力，例如：

- 行情快照、K 线、Tick
- 股票、板块、财务和更多信息
- 公式系统
- 自选股与板块操作

因此这条分支的正确方向不是继续扩张“纯桌面自动化脚本”，而是建立一个 Windows bridge：

- 对数据、公式等稳定能力，优先走 TdxQuant 官方接口
- 对交易执行等桌面环节，继续走 Win32/UIA + HID
- 对 WSL 侧，统一暴露一个稳定调用面

## Goals / Non-Goals

**Goals:**
- 为 WSL 侧策略脚本提供统一的 Windows TDX 调用入口。
- 把“数据读取”和“交易执行”拆成两条技术路线，并在同一 bridge 中整合。
- 优先交付非 GUI 数据能力，降低对桌面状态和人工值守的依赖。
- 在交易链路上保留现有 Win32/UIA 探测资产，并通过 HID 完成代码输入闭环验证。
- 为后续卖出、撤单、持仓查询、自选股管理和事件推送预留可扩展结构。

**Non-Goals:**
- 本次不要求一次性实现 TdxQuant 官方接口的全部函数。
- 本次不要求实现完整的实盘交易生命周期管理。
- 本次不要求让 WSL 直接调用 Win32；桌面操作仍限定在 Windows 原生 Python 环境。
- 本次不要求先解决多客户端、多账户和多窗口并行管理问题。
- 本次不要求处理红宝书系列文档的重新转换和全文知识抽取。

## Decisions

### 1. 建立 Windows sidecar，而不是让 WSL 直接碰桌面

WSL 不适合直接操作 Windows GUI，也不应直接承担 HID 串口和桌面窗口管理。因此需要一个 Windows sidecar 进程或命令层作为唯一执行面。

推荐职责：

- 探测通达信客户端状态
- 调用 TdxQuant 官方 Python 接口
- 处理 Win32/UIA/HID 操作
- 返回结构化 JSON 给 WSL 侧

备选方案：
- 让 WSL 通过零散 `python.exe -m ...` 命令直接驱动 Windows 端脚本。短期可行，但接口松散、状态不可控、后续难扩展。

### 2. 数据能力优先走官方 TdxQuant Python 接口

快照、K 线、财务、板块和公式等能力，本质上不应该通过 GUI 抓取实现。GUI 只用于交易页面和客户端状态归因。

第一批优先能力应包括：

- `health`
- `tdx_status`
- `get_market_snapshot`
- `get_kline`
- `get_stock_info`
- `get_sector_list`

备选方案：
- 继续优先做桌面菜单点击、表格抓取。回报率低，且和官方接口能力重复。

### 3. 公式系统作为独立 capability，而不是塞进数据接口

公式系统与普通数据读取的使用模式不同，涉及：

- 格式化数据
- 设置公式输入数据
- 调用指标/选股/专家系统
- 批量处理

因此应单独定义 `tdx-formula-bridge`，避免后续 API 语义混乱。

### 4. 交易自动化继续采用 Win32/UIA + HID 组合

现有验证已经表明：

- Win32/UIA 适合探测、定位、读回、按钮触发和弹窗抓取
- HID 适合补齐证券代码输入

因此交易 capability 不再追求“纯后台消息完成整单”，而是明确采用混合路线。

第一阶段交易目标：

- 买入页探测
- 焦点和前台校验
- HID 输入证券代码
- Win32 填价格/数量
- Win32 触发提交
- 抓取确认/提示弹窗

### 5. 统一输出结构，所有 bridge 命令都返回 JSON

不论底层走官方接口还是 GUI/HID，返回结构都应至少包含：

- `ok`
- `code`
- `message`
- `data`
- `warnings`
- `next_action`

这样 WSL 侧策略才能稳定消费，不依赖文本解析。

### 6. 首轮 bridge 形态优先采用 CLI-compatible 命令层

当前仓库已经以 `python -m tdxquant.cli` 为主入口。为了快速复用，首轮 bridge 可以先保持 CLI-compatible，后续如需要再封装成常驻 HTTP/IPC 服务。

好处：

- 复用现有命令和测试方式
- 降低首轮实现成本
- 方便用户手工验证

后续如果 WSL 调用频率和状态管理需求上来，再演进到 sidecar service。

## Risks / Trade-offs

- [官方 TdxQuant 接口在当前 Windows 环境不可直接调用] → 先做探测和最小调用样例，再扩展更多函数。
- [WSL 到 Windows 的调用协议过早复杂化] → 首轮先维持 CLI-compatible JSON 输出，不先上复杂服务框架。
- [通达信句柄映射跨会话变化] → 保留 `probe` 和 `inspect` 命令，避免把固定句柄当成永久真理。
- [HID 设备输入打到错误窗口] → 在交易命令前强制做前台窗口和焦点校验。
- [官方接口与 GUI 状态不一致] → 区分“数据桥接”和“交易桥接”，不要把两者混成同一状态机。
- [文档来源质量不一致] → 以接口说明文档和实测结果为准，暂不依赖转换质量差的红宝书文档做实现依据。

## Migration Plan

1. 新增专门的 TDX bridge OpenSpec 规格和任务拆分。
2. 在现有 `tdxquant` 包中抽出 bridge 相关模型和命令分组。
3. 先落地最小健康检查和数据接口桥接。
4. 再落地公式桥接。
5. 最后把现有通达信 HID/Win32 买入探测链路纳入统一 bridge。
6. 在真实 Windows 环境中验证数据接口、HID 输入和交易提示链路。

## Open Questions

- Windows bridge 最终是以命令层存在，还是升级为常驻 HTTP/IPC sidecar 服务？
- 当前 Windows 端 TdxQuant 官方 Python 环境和通达信客户端版本是否完全匹配？
- 官方接口是否已经覆盖持仓、委托、成交和撤单，还是仍需 GUI 辅助？
- 自选股和板块管理应放进第一阶段，还是推迟到数据和公式能力稳定后再做？
- 如果同时存在多个通达信窗口，bridge 如何稳定选择目标实例？
