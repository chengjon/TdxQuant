# 通达信 Windows Bridge 开发说明

日期：2026-04-24

## 1. 目标

本仓库当前的通达信主线目标是打通：

- WSL 侧策略或脚本
- Windows 原生 Python 执行层
- 通达信客户端与 TdxQuant 运行时
- 必要时的 HID 硬件键盘桥接

设计原则：

- 数据与公式优先走官方 `TdxQuant` Python 接口。
- 交易执行优先走 `Win32/UIA + HID` 混合链路。
- 所有 bridge 命令统一返回 JSON 包装结构。
- WSL 不直接执行 Win32、UIA、串口或 HID 操作。

## 2. 推荐的第一批命令

### 2.1 健康检查

```bash
python -m tdxquant.cli tdx-bridge-health --window-key 通达信金融终端 --hid-port COM3
```

用途：

- 检查是否处于原生 Windows Python
- 检查 TdxQuant 运行时能否初始化
- 检查通达信主窗口是否可见
- 检查 HID 串口是否可枚举

### 2.2 数据桥接

```bash
python -m tdxquant.cli tdx-data-snapshot --code 000001
python -m tdxquant.cli tdx-data-kline --code 000001 --period 1d --count 20
python -m tdxquant.cli tdx-data-stock-info --code 000001
python -m tdxquant.cli tdx-data-sector-list
python -m tdxquant.cli tdx-data-sector-stocks --sector 880318
```

用途：

- 统一从 TdxQuant 读取快照、K 线、股票信息和板块信息
- 让 WSL 侧不用解析文本和桌面控件

### 2.3 公式桥接

```bash
python -m tdxquant.cli tdx-formula-zb --formula-name MA --formula-arg "N=5"
python -m tdxquant.cli tdx-formula-xg --formula-name "<选股公式名>"
python -m tdxquant.cli tdx-formula-exp --formula-name "<专家公式名>"
python -m tdxquant.cli tdx-formula-mul-zb --formula-name MA --formula-arg "N=5" --code 000001 --count 20
python -m tdxquant.cli tdx-formula-set-data-info --code 000001 --stock-period 1d --count 50
```

用途：

- 统一桥接指标、选股、专家公式与批量公式
- 统一桥接公式运行前的数据准备动作

说明：

- 当前实现对公式接口采用动态兼容层。
- 如果 Windows 端实际运行时没有暴露某个方法，会返回明确错误，不会静默假成功。

### 2.4 交易 / HID bridge

```bash
python -m tdxquant.cli tdx-trade-probe --window-key 通达信金融终端
python -m tdxquant.cli tdx-trade-hid-ping --port COM3
python -m tdxquant.cli tdx-trade-hid-send --port COM3 --wire-command "TYPE 000001 TAB"
python -m tdxquant.cli tdx-trade-buy-probe --window-key 通达信金融终端 --port COM3 --code 000001 --price 10.00 --quantity 100 --pre-clear --commit-key tab --submit-strategy post_wm_command_parent
```

用途：

- `tdx-trade-probe`：统一输出买入页句柄、证据和控件可读状态
- `tdx-trade-hid-ping`：检查 HID 串口链路
- `tdx-trade-hid-send`：只允许最小协议集 `PING / KEY / TYPE`
- `tdx-trade-buy-probe`：走完整的低风险买入探测链路

## 3. 运行边界

### 3.1 必须在 Windows 原生 Python 执行的能力

- `tdx-bridge-health`
- 所有 `tdx-data-*`
- 所有 `tdx-formula-*`
- 所有 `tdx-trade-*`
- 所有 `win32-*`
- 所有 `uia-*`

原因：

- `pywin32`
- `pywinauto / UIA`
- `pyserial`
- TdxQuant Windows 运行时

这些都属于 Windows 本地能力，不应由 WSL 直接驱动。

### 3.2 WSL 侧负责什么

- 组织参数
- 调用 Windows Python
- 落盘 JSON
- 解析统一结果结构：
  - `ok`
  - `code`
  - `message`
  - `data`
  - `warnings`
  - `next_action`

## 4. 当前结论

### 4.1 已经可用

- TdxQuant 数据 bridge
- TdxQuant 公式 bridge
- 通达信买入页 probe
- HID 串口协议客户端
- HID + Win32 的买入探测半闭环

### 4.2 仍待真实环境确认

- HID 输入后是否稳定越过“请输入证券代码!”
- 提交后是否始终进入真实确认弹窗
- 不同通达信版本下固定句柄是否需要重新探测

## 5. 推荐验证顺序

1. 先跑 `tdx-bridge-health`
2. 再跑 `tdx-data-snapshot`
3. 再跑 `tdx-formula-zb`
4. 再跑 `tdx-trade-probe`
5. 再跑 `tdx-trade-hid-ping`
6. 再跑 `tdx-trade-hid-send`
7. 最后跑 `tdx-trade-buy-probe`

## 6. 低风险约束

- 买入探测必须继续使用明显不能即时成交的低价
- `tdx-trade-buy-probe` 的首选用途是验证链路，不是直接做可成交委托
- 交易线出现焦点异常、窗口未置前、句柄失效时，应立即停止继续发送 HID

## 7. 文档源质量限制

当前开发依据按优先级排序如下：

1. `/mnt/wd_mycode/tdxquant/tdx-docs/TdxQuant接口说明文档.md`
2. 本仓库中的真实联调记录和导出样本
3. 通达信客户端实时行为观察

以下资料当前不直接作为实现依据：

- 转换质量较差的“红宝书”文档
- OCR 失真严重、表格丢失、代码段破碎的二次转换文档

原因：

- 接口名、参数名和返回结构容易失真
- 误导实现的风险高于提供价值

## 8. 后续扩展列表

当前建议继续开发的下一批功能：

- 卖出页 probe 与 HID buy/sell 对称命令
- 撤单页 probe
- 持仓与委托查询 bridge
- 自选股与板块管理 bridge
- WSL 侧统一调用脚本或 sidecar 封装
