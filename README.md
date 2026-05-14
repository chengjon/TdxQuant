> 功能状态入口：当前项目的唯一“功能全景图 + 状态注册表”是 [`FUNCTION_TREE.md`](FUNCTION_TREE.md)。
>
> 本 README 只说明当前分支定位和常用入口；具体功能是否已实现、部分实现、已设计待实现或属于非目标边界，以 `FUNCTION_TREE.md` 为准。

## 当前分支定位

这条分支当前以 `WSL <-> Windows TDX bridge` 为主目标。

- 数据与公式能力优先走 Windows 原生 `TdxQuant` Python 接口。
- 交易能力优先走 `Win32/UIA + HID` 混合路线。
- WSL 侧只消费结构化 JSON 结果，不直接碰 Win32、UIA 或 HID。

当前推荐的第一批 bridge 命令：

```bash
python -m tdxquant.cli tdx-bridge-health --window-key 通达信金融终端 --hid-port COM3
python -m tdxquant.cli tdx-data-snapshot --code 000001
python -m tdxquant.cli tdx-data-kline --code 000001 --period 1d --count 20
python -m tdxquant.cli tdx-formula-zb --formula-name MA --formula-arg "N=5"
python -m tdxquant.cli tdx-trade-probe --window-key 通达信金融终端
python -m tdxquant.cli tdx-trade-hid-ping --port COM3
python -m tdxquant.cli tdx-trade-hid-send --port COM3 --wire-command "TYPE 000001 TAB"
python -m tdxquant.cli tdx-trade-buy-probe --window-key 通达信金融终端 --port COM3 --code 000001 --price 10.00 --quantity 100 --pre-clear --commit-key tab --submit-strategy post_wm_command_parent
```

文档依据说明：

- 主要实现依据是 `tdx-docs/TdxQuant接口说明文档.md` 和真实客户端联调结果。
- 转换质量较差的“红宝书”类文档只可作背景参考，当前不直接作为开发依据。

TdxQuant 简介
https://help.tdx.com.cn/quant/docs/
https://help.tdx.com.cn/book.html

正式版 下载通达信专业研究版
https://www.tdx.com.cn/soft.html

#1.2安装后登录通达信

TdxQuant是由深圳市财富趋势科技股份有限公司研发的专业量化投研平台，专注于为国内量化投资者提供从策略研究到投资决策的全流程解决方案。平台以高效、简洁为核心设计理念，致力于降低量化交易门槛，提升策略开发与执行的效率。

依托通达信近三十余年在金融科技领域的深厚积累，TdxQuant集成了完备的实时和历史行情数据、金融数据库及稳定的交易系统基础设施，为策略的研发、回测、验证和执行提供了坚实可靠的技术支持。

平台采用分层化、模块化的服务体系，可灵活适配从高校学生、独立研究者、个人投资者到专业机构等不同用户的需求，实现从策略构思到交易落地的无缝衔接。

#TdxQuant 服务介绍
TdxQuant 是一套基于通达信金融终端构建的 Python 量化策略运行框架。该框架通过 API 接口形式，为策略交易提供所需的行情数据获取与交易指令执行功能。

#运行环境要求
TdxQuant 支持 64 位 Python 3.7、3.8、3.9、3.10、3.11、3.12、3.13等版本，系统会自动适配当前 Python 版本，建议使用3.13版本。
请注意：运行 TdxQuant 程序前，需预先启动支持TQ策略功能的 通达信金融终端、专业研究版等版本。

#核心运行逻辑
TdxQuant 以 tqcenter 行情模块为核心，专注于为量化交易者提供高效、直接的数据服务，主要包含以下内容：

行情数据：实时与历史的快照、K 线、分笔（Tick）数据
基本面数据：除权除息、基本财务、专业财务、股票交易数据、市场数据等
新股和合约等信息：标的基础信息、可转债、新股申购等
分类数据：市场类型、行业分类、自定义板块等
#核心应用场景
TdxQuant提供覆盖量化投研全流程的核心功能模块，主要应用场景包括：

#1. 策略研发与历史回测
平台提供“即用型”标准化数据。所有历史与实时数据均在服务端完成清洗、对齐，并预加载至客户端。支持用户快速获取指定时间维度的历史数据，并进行策略信号计算与回测分析。既提供复权因子，也提供各种类型的复权后的数据。

#2. 实时监控与信号预警
支持实时行情数据订阅，用户可基于自定义的指标与因子模型进行在线计算。当预设条件触发时，系统通过信号接口实时推送预警信息至客户端，助力研究者及时捕捉市场动态与交易机会。

#3. 交易模拟与实盘执行
平台构建了完整的策略交易闭环，提供模拟交易、券商实盘等两种执行环境：

模拟交易：在仿真市场环境中，使用实时行情数据对策略进行持续跟踪与验证，评估其实际表现，全程无资金风险。
实盘交易：通过稳定的交易总线，安全对接券商报盘系统，实现策略信号的自动化、高可靠性下单与交易管理。
#量化交易的核心价值
#1. 利用历史数据高效验证策略，提升研究效率数百倍
在验证交易策略时，历史回测是评估其有效性的关键环节，但传统人工方式难以处理海量数据与复杂计算。量化交易可在几分钟内完成一次全面回测，快速获得统计验证结果，极大提升了策略研发的迭代效率。

#2. 实时捕捉基于概率的获胜机会
量化交易借助计算机强大的数据处理能力，能够从海量市场信息中发掘人工难以察觉的规律与机会。面对全市场数千只股票的实时波动，量化系统可同时监控多重条件，避免机会错失。它能够综合考量选股、择时、资产配置与风险管理，构建并执行具有较大概率的投资组合，追求收益最大化。

#3. 实现科学、客观的投资决策
与传统主观投资不同，量化交易将投资理念、经验甚至市场直觉转化为严谨的数学模型。通过系统化的信号生成与执行机制，有效克服人性中的情绪偏差，使投资决策过程更具纪律性、可重复性与可优化性。

#量化交易的工具挑战
工欲善其事，必先利其器。 对于个人投资者而言，独立搭建一套完整的量化交易体系，复杂繁琐，涉及数据、系统、策略等多层面的巨大投入。

#一、需要准确、全面的金融数据基础
量化交易依赖于高质量的历史与实时数据，包括行情、财务、宏观及基本面数据等。构建和维护这样一个数据仓库，不仅需要持续的数据采购、清洗、更新与运维成本，还需在数据存储、访问速度与系统稳定性方面进行深入的技术投入。

#二、需要易用、可靠的量化交易系统
一个成熟的量化平台需要支持多样的策略开发语言、具备高速的回测与模拟引擎、提供科学的策略评估体系，并为实盘交易提供全方位的保障。过往，研究者往往需要兼具复杂的金融数据知识与工程构建能力。如今，TdxQuant让您只需专注于策略逻辑本身，其余复杂工作交给平台。

#TdxQuant的核心优势
TdxQuant是一款集金融数据与策略投研工具于一体的量化平台，结构清晰，简洁易上手，数据获取快捷，算法资源丰富。我们的目标是为投资者提供"开箱即用"的完整解决方案。

#1. 全方位保障策略安全与自主
支持策略在本地IDE环境中开发与运行，保障代码安全与私密性
分离式模块化架构，策略的编码和调试更加自由和灵活
#2. 大幅降低量化交易门槛
提供高质量、高精度、快速接入的金融元数据
支持多种策略类型的便捷编写、回测、模拟与实盘
#3. 助力构建专业量化成长路径
通过"投资学院"系统学习量化交易相关知识体系
通过"宽客社区"交流心得、解答疑惑
全程助力用户从入门到精通，成为专业的量化投资者

## Ping An Win32 Adapter

说明：

- 这一节保留的是平安证券与早期 Win32/UIA 试验记录。
- 当前主线开发已转向通达信 bridge；平安证券不再作为本分支的主目标。

仓库中新增了一个面向平安证券客户端的 Win32 后台交易适配骨架，入口为 `python -m tdxquant.cli`。

### 运行前提

- 真实的 Win32 控件探测和下单必须在原生 Windows Python 下执行。
- WSL/Linux 可以做路径发现和文档开发，但不能直接调用 `pywin32` 去枚举窗口或发送消息。
- 默认支持的安装路径包括：
- Windows: `D:\ProgramData\PinganSec\TdxW.exe`
- WSL: `/mnt/d/ProgramData/PinganSec/TdxW.exe`

### 安装依赖

```bash
pip install -r requirements.txt
```

`pywin32` 只会在 Windows 上安装。

### 命令

```bash
python -m tdxquant.cli health-check
python -m tdxquant.cli inspect
python -m tdxquant.cli inspect --output artifacts/pingan-controls.json
python -m tdxquant.cli uia-windows --output artifacts/pingan-windows.json
python -m tdxquant.cli uia-inspect --max-depth 8 --output artifacts/pingan-uia.json
python -m tdxquant.cli uia-click --automation-id 1033 --post-delay 1.0
python -m tdxquant.cli uia-click-path --path 0/17/0/0/0/1/6 --post-delay 1.0
python -m tdxquant.cli uia-click-center --automation-id 2010 --control-type Button --post-delay 1.0
python -m tdxquant.cli uia-activate --automation-id 2010 --control-type Button --strategy wm_command --post-delay 1.0
python -m tdxquant.cli uia-set-text --automation-id 12005 --value 000001
python -m tdxquant.cli uia-read --automation-id 2021 --control-type Text
python -m tdxquant.cli uia-combobox-items --automation-id 10020
python -m tdxquant.cli uia-combobox-select --automation-id 10020 --item-name "<选项文本>"
python -m tdxquant.cli detect
python -m tdxquant.cli detect-snapshot --snapshot artifacts/pingan-controls.json
python -m tdxquant.cli uia-detect-snapshot --snapshot artifacts/pingan-uia.json
python -m tdxquant.cli pingan-probe --code 000001 --price 10.00 --quantity 100 --output artifacts/pingan-probe.json
python -m tdxquant.cli hid-ping --port COM3
python -m tdxquant.cli hid-send --port COM3 --wire-command "TYPE 000001 TAB"
python -m tdxquant.cli tdx-hid-buy-probe --title-key 通达信金融终端 --window-key 通达信金融终端 --port COM3 --code 000001 --price 10.00 --quantity 100 --pre-clear --commit-key tab --submit-strategy post_wm_command_parent
python -m tdxquant.cli buy --code 000001 --quantity 100 --price 12.34 --dry-run
```

可选参数：

- `--exe-path`：显式指定 `TdxW.exe` 的 Windows 或 WSL 路径
- `--title-key`：覆盖默认窗口标题关键词，默认值为 `平安证券`
- `--output`：把结构化 JSON 结果写到文件，便于保存控件树样本
- `uia-windows`：枚举桌面当前顶层 UIA 窗口，适合抓独立确认框或无标题对话框
- `uia-click`：按 `automation_id` 或文本点击 UIA 节点
- `uia-click-path`：按 `uia-inspect` 导出的节点路径精确点击 UIA 节点
- `uia-click-center`：按控件矩形中心的屏幕坐标做真实鼠标点击
- `uia-activate`：对按钮等控件按多策略激活，可用 `--strategy auto|invoke|click_input|bm_click|wm_command|enter_key`
- `uia-set-text`：按 `automation_id` 或文本给 UIA 输入控件写值，默认控件类型为 `Edit`
- `uia-read`：读回指定 UIA 节点的当前状态，包括 `window_text`、`rich_text`、`legacy_value`、`handle`
- `uia-combobox-items`：读取指定 UIA 下拉框的候选项
- `uia-combobox-select`：按文本选择指定 UIA 下拉框项
- `pingan-probe`：一键执行平安证券纯非物理买入探测链路，自动完成填值、依次尝试 `invoke/bm_click/wm_command/enter_key`、前后读回、窗口枚举、UIA 快照
- `pingan-buy-submit-once`：自动完成平安证券买入下单、推进确认、关闭结果窗；执行完成后主界面恢复到可继续下一单的状态，并把合同号回填到命令 JSON、`runtime/pingan-last-order.json` 和 stderr 日志
- `pingan-buy`：`pingan-buy-submit-once` 的高层封装命令，固定流程并提供 `stable|balanced|fast` 三档 profile；支持少量常用参数和高级延时覆盖，并在结果 JSON 中输出 `timing` 耗时信息
- `hid-ping`：对 Arduino HID 桥接设备发送 `PING`，确认串口和协议正常
- `hid-send`：向 HID 设备发送单条串口协议命令，例如 `KEY CTRL+A` 或 `TYPE 000001 TAB`
- `tdx-hid-buy-probe`：复用现有通达信 Win32 探测、填价、填量和提交链路，但把证券代码输入替换为 HID 真实键盘输入

### 通达信 HID 路线

当前仓库已经落地最小 HID 原型：

- Windows 主机侧协议客户端：`tdxquant/hid_bridge.py`
- Arduino 固件样例：`firmware/arduino/tdx_hid_keyboard/tdx_hid_keyboard.ino`
- 方案说明：`docs/tdx-hid-keyboard-plan.md`

当前支持的串口协议：

- `PING`
- `KEY TAB`
- `KEY ENTER`
- `KEY ESC`
- `KEY DELETE`
- `KEY CTRL+A`
- `TYPE 000001`
- `TYPE 000001 TAB`
- `TYPE 000001 ENTER`

建议首次验证顺序：

1. 给 Leonardo/Micro 刷写 `firmware/arduino/tdx_hid_keyboard/tdx_hid_keyboard.ino`
2. 在 Windows 下运行 `python -m tdxquant.cli hid-ping --port COM3`
3. 打开通达信买入页并手工确认代码框可见
4. 运行 `python -m tdxquant.cli tdx-hid-buy-probe --title-key 通达信金融终端 --window-key 通达信金融终端 --port COM3 --code 000001 --price 10.00 --quantity 100 --pre-clear --commit-key tab --submit-strategy post_wm_command_parent`
5. 观察提交后弹窗是否已越过 `请输入证券代码!`

平安证券当前版本已确认的买入区原生控件：

- `12005`：证券代码输入框
- `12006`：买入价格输入框
- `12007`：买入数量输入框
- `12015`：股东代码/账号下拉框
- `1129`：报价方式下拉框
- `2010`：`买入下单` 按钮

UIA 执行命令现在会先尝试恢复并前置主窗口，避免交易面板落到离屏/最小化坐标。

`pingan-buy-submit-once` 成功提交后的回填产物：

- `--output` 指定的结果 JSON：`data.result_dialog.contract_no`
- 固定状态文件：`runtime/pingan-last-order.json`
- 命令日志：stderr 输出 `[pingan-buy-submit-once] contract_no=<合同号>`

### 平安证券实测结论

基于当前实测的平安证券慧赢客户端版本，这条自动化链路的能力边界已经比较明确：

- 已验证可稳定发现运行入口与主窗口，兼容 Windows 路径与 WSL 路径映射。
- 已验证可稳定枚举 UIA 树，并定位买入区原生控件。
- 已验证可稳定向买入区写入：
  - `12005` 证券代码
  - `12006` 买入价格
  - `12007` 买入数量
- 已验证可稳定读回买入区状态：
  - `2021` 证券名称/联动文本
  - `2022` 数量/可买联动文本
  - `9100` 预估金额
- 已验证 `12015` 当前值为 `深A 0118727906`，`1129` 当前值为 `限价委托`，它们本身不是明显的阻塞点。

纯非物理提交能力的最终结论：

- 已测试 `invoke`
- 已测试 `bm_click`
- 已测试 `wm_command`
- 已测试 `enter_key`
- 以上非物理策略都能命中按钮链路，但都只能触发买入面板内部的局部状态清空/刷新，未进入确认框、委托确认或报单结果流程。
- 因此，对当前这个平安证券客户端版本，`读值/填值/状态探测` 是可行的，`纯非物理最终提交` 目前不可确认可行，工程上应视为未打通。

建议的工程结论：

- 若要求“不能使用物理点击”，则平安证券当前线路应收口为“填单与状态探测工具”，不要宣称已支持最终下单。
- 若后续目标是纯非物理实盘提交流程，建议切换到更接近标准 Win32 交易窗的客户端继续验证，例如通达信经典交易窗。

推荐验证闭环：

1. 在 Windows 里运行 `python -m tdxquant.cli inspect --output pingan-controls.json`
2. 如果页面疑似 WebView，再运行 `python -m tdxquant.cli uia-inspect --max-depth 8 --output pingan-uia.json`
3. 把 `pingan-controls.json` 和 `pingan-uia.json` 带回当前仓库
4. 在任意环境运行 `python -m tdxquant.cli detect-snapshot --snapshot pingan-controls.json`
5. 在任意环境运行 `python -m tdxquant.cli uia-detect-snapshot --snapshot pingan-uia.json`
6. 根据 Win32 和 UIA 两份结果选择后续自动化路线

### 当前实现边界

- 已实现路径解析、结构化结果、Win32 探测接口、买入 dry-run 入口和基础控件匹配。
- 当前匹配器已经会结合相邻标签、同父控件顺序和矩形位置做推断，但仍需要拿真实客户端的 `inspect` 输出做最后收敛。
- 对 WebView 版本客户端，已新增 UIA 探测与离线分析命令，用于判断 HTML 输入框和按钮是否暴露给 Windows 无障碍树。
- 对通达信线路，已新增 HID 串口桥接和 `tdx-hid-buy-probe` 命令，用于只替换证券代码输入这一个阻塞环节。
- 当前尚未处理买入后的确认弹窗、风控提示、委托回报查询、卖出和撤单。
- `inspect`、`detect`、`buy` 在 WSL/Linux 下会返回 `unsupported_platform`，这是预期行为。
