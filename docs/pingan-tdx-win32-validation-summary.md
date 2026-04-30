# 平安证券 / 通达信 Win32 联调总结

## 1. 目标

基于 [pa-sect-read.md](/opt/iflow/TdxQuant/docs/pa-sect-read.md) 的思路，验证以下能力是否能在真实客户端上成立：

- 发现交易客户端路径与主窗口
- 探测交易页控件树
- 非物理写入证券代码、价格、数量
- 非物理触发“买入下单”
- 如出现确认/提示弹窗，继续用非物理方式处理

用户约束很明确：

- 不接受人工物理点击
- 不接受依赖屏幕坐标的“真鼠标点击”作为最终方案
- 可以接受 Win32/UIA 级别的非物理自动化

本次联调的核心问题不是“能否找到按钮”，而是：

- 券商客户端是否接受纯 Win32 后台消息作为完整下单链路


## 2. 环境与对象

### 2.1 仓库

- 工作目录：`/opt/iflow/TdxQuant`
- Windows 运行副本：`/mnt/d/MyCode3/tdx`

### 2.2 客户端

- 平安证券真实路径：`D:\ProgramData\PinganSec\TdxW.exe`
- WSL 映射路径：`/mnt/d/ProgramData/PinganSec/TdxW.exe`
- 通达信真实路径：`D:\mystocks\tdx\tdx_new\tdxw.exe`

### 2.3 代码改动范围

本次联调期间，已在 `tdxquant` 工具层新增或补强以下能力：

- UIA 枚举：`uia-windows`、`uia-inspect`、`uia-dialogs`、`uia-wait-dialog`
- Win32 句柄级操作：`win32-read`、`win32-set-text`、`win32-type-text`、`win32-click`
- 通达信专项探测：`tdx-probe`、`tdx-buy-probe`、`tdx-submit-probe`、`tdx-submit-once`
- 底层消息补强：
  - `WM_GETTEXT` 优先读跨进程 `Edit`
  - `BM_CLICK`
  - `WM_COMMAND` / `PostMessage(WM_COMMAND)`
  - `WM_CHAR`
  - `Enter` / `Tab` / `Space`


## 3. 方法论

本次不是直接写“买入脚本”，而是按下面的顺序推进：

1. 路径发现
2. 主窗口发现
3. 导出控件树
4. 固化关键控件句柄
5. 分别验证字段写入、字段读回、按钮触发
6. 对出现的弹窗继续做句柄级探测
7. 只在低价不成交前提下验证完整链路

这样做的原因是：

- 券商客户端对后台消息的接受程度高度版本相关
- “控件能读到文本”不等于“业务层认可该输入”
- “按钮能收到消息”不等于“交易逻辑真的执行”


## 4. 平安证券线路

### 4.1 已验证能力

平安证券当前版本可以稳定完成：

- 主窗口发现
- 控件树导出
- 买入页关键控件识别
- 非物理填充字段
- 部分状态文本读取

换句话说，平安证券这条线已经证明：

- 可探测
- 可识别
- 可填单
- 可读状态

### 4.2 已打通的最终提交链路

在引入 HID 键盘桥后，平安证券这条线已经验证出稳定的真实买入闭环。

已验证成功的策略组合：

- 填单阶段：UIA 直接写入
  - 证券代码：`12005`
  - 买入价格：`12006`
  - 买入数量：`12007`
- 首次触发确认：HID `Tab + Enter`
- 买入确认窗推进：`WM_COMMAND`
- 结果提示窗关闭：HID `Enter`

关键现象：

- 仅靠 `UIA Invoke` / `BM_CLICK` / 纯 UIA 路径点击，无法稳定穿透买入确认
- “买入交易确认”窗口中的 `买入确认(7015)` 在业务上接受 `WM_COMMAND`
- 成功推进后会出现 `提示` 窗口，正文为 `委托已提交，合同号 XXX`
- 该 `提示` 窗口的 `确认(7015)` 最稳关闭方式是 HID `Enter`

### 4.3 已验证样本

最终用于打通闭环的真实样本：

- 证券代码：`516820`
- 名称：`医疗创新ETF平安`
- 买入价格：`0.35`
- 买入数量：`100`

链路结果：

- 成功进入 `买入交易确认`
- 成功推进到 `提示：委托已提交，合同号 XXX`
- 成功关闭结果窗
- 主窗口恢复 `enabled: true`

关键证据文件：

- `/mnt/d/MyCode3/tdx/pingan-516820-submit-once.json`
- `/mnt/d/MyCode3/tdx/pingan-after-submit-uia-v2.json`
- `/mnt/d/MyCode3/tdx/pingan-result-hid-enter.json`
- `/mnt/d/MyCode3/tdx/pingan-result-after-hid-enter.json`
- `/mnt/d/MyCode3/tdx/pingan-v2-result-hid-enter.json`
- `/mnt/d/MyCode3/tdx/pingan-v2-after-hid-enter.json`

### 4.4 结论

平安证券当前版本的最终结论已更新为：

- 在“不接受人工物理点击”的约束下，可实现自动买入闭环
- 但最终方案不是“纯后台 Win32 消息”，而是混合链路：
  - UIA 写值
  - Win32 `WM_COMMAND`
  - HID 真实键盘输入

因此平安证券线路现在应视为：

- 已满足最终目标
- 可作为当前项目的可用交易自动化实现


## 5. 通达信线路

### 5.1 固化出的关键句柄

在真实通达信买入页上，识别到以下关键控件：

- 代码框：`hwnd=725916`，`control_id=12005`
- 价格框：`hwnd=398452`，`control_id=12006`
- 数量框：`hwnd=592962`，`control_id=8088`
- 买入按钮：`hwnd=331326`，`control_id=2010`，文本 `买入下单`

关键父链路：

- 买入按钮父窗口：`parent_hwnd=1709156`
- 这也是买入页字段所在的核心父容器

### 5.2 已验证能力

通达信线路目前已经稳定验证出：

- 代码、价格、数量字段都可以非物理写入
- 三个字段都可以用 Win32 读回
- 买入按钮可被非物理触发
- `post_wm_command_parent` 能稳定触发业务提示弹窗

### 5.3 关键尝试过程

#### A. 提交按钮策略验证

对 `买入下单(hwnd=331326)`，尝试过多种提交方式：

- `bm_click`
- `wm_command_parent`
- `post_wm_command_parent`
- `enter_key`
- `space_key`
- `mouse_message`
- `wm_command_ancestor_N`
- `post_wm_command_ancestor_N`

主要发现：

- 某些祖先级 `WM_COMMAND` 会把主窗口切到 `分析图表-协鑫集成`
- 这类策略不是正常下单确认链路，而是消息被打到了主框架
- `post_wm_command_parent` 是目前最接近正确业务链路的触发方式

#### B. 代码输入策略验证

对代码框尝试过四类输入方法：

1. `WM_SETTEXT`
2. `WM_CHAR` 逐字符输入
3. 输入后再发 `Tab`
4. 前台 `keybd_event` 键盘事件链：聚焦、`Ctrl+A`、`Delete`、逐字符输入、`Tab`

字段层面的结果是：

- `000001` 可以写入
- 也可以稳定读回

但业务层的结果是：

- 弹窗正文始终是 `请输入证券代码!`

这说明：

- 窗口控件层“有文本”
- 不代表通达信交易逻辑认可“证券代码已完成有效输入”

#### C. `Stock` 注册消息验证

本次还验证了通达信更底层的注册消息路线：

- `RegisterWindowMessage("Stock")`
- `PostMessage(main_hwnd, UWM_STOCK, stock_value, 0)`

对 `000001` 的深市编码值：

- `6000001`

验证结果：

- 发送前主窗口标题是 `分析图表-协鑫集成`
- 发送后主窗口标题稳定切换为 `分析图表-平安银行`

因此可以确认：

- `Stock` 注册消息本身有效
- 它可以稳定切换通达信主窗口当前证券上下文

但把它接入交易链路后，结果仍然是：

- 只靠 `Stock` 消息切到 `平安银行`
- 再只填价格和数量并非物理触发 `买入下单`
- 弹窗正文仍然是 `请输入证券代码!`

所以可以明确：

- `Stock` 消息适合做切图/切主证券上下文
- 但不能替代交易页“证券代码输入”本身

### 5.4 弹窗证据

多次抓取 `提示` 弹窗后，稳定得到相同结果：

- 按钮：
  - `确认`
  - `取消`
  - `放弃`
- 正文：
  - `请输入证券代码!`

典型证据文件：

- `/mnt/d/MyCode3/tdx/tdx-prompt-controls.json`
- `/mnt/d/MyCode3/tdx/tdx-confirm-controls.json`
- `/mnt/d/MyCode3/tdx/tdx-confirm2-controls.json`
- `/mnt/d/MyCode3/tdx/tdx-stock-context-popup-controls.json`
- `/mnt/d/MyCode3/tdx/tdx-keybd-popup-controls.json`

这三轮抓取都说明同一件事：

- 当前卡点不是“确认按钮怎么点”
- 而是“证券代码输入未被业务层接受”

新增两轮抓取进一步补强为：

- 即使主窗口已经通过 `Stock` 注册消息切到 `平安银行`
- 即使代码框采用 `keybd_event` 风格的前台键盘事件链
- 弹窗正文仍然可以稳定复现 `请输入证券代码!`

### 5.5 已排除的误判

本次联调中还排除了几个容易误判的方向：

- 不是“买入按钮无效”
  - 因为 `post_wm_command_parent` 可以稳定弹出业务提示
- 不是“弹窗抓不到”
  - 因为 Win32 控件树能读出按钮和正文
- 不是“字段没写进去”
  - 因为代码/价格/数量都能稳定读回
- 不是“只是旧弹窗残留”
  - 清理后重跑，仍然得到 `请输入证券代码!`
- 不是“主证券上下文不对”
  - 因为 `Stock` 注册消息已验证能把主窗口从 `协鑫集成` 切到 `平安银行`
- 不是“只差更像真实键盘的输入链”
  - 因为 `keybd_event + Ctrl+A + Delete + 逐字符输入 + Tab` 仍然失败


## 6. 实际使用说明

### 6.1 前置条件

执行平安证券自动买入前，必须满足：

- 平安证券已登录并处于可交易状态
- Windows 侧代码副本已同步到 `D:\MyCode3\tdx`
- HID 键盘桥可用，例如 `COM3`
- 当前桌面不要让无关窗口反复抢焦点

建议每次交易前先检查 HID：

```powershell
python -m tdxquant.cli hid-ping --port COM3 --output hid-ping.json
```

### 6.2 标准命令模板

```powershell
python -m tdxquant.cli --exe-path D:\ProgramData\PinganSec\TdxW.exe --title-key "平安证券" pingan-buy-submit-once --port COM3 --hid-pre-delay 3 --code <证券代码> --price <买入价格> --quantity <买入数量> --post-delay 1.0 --max-depth 12 --dialog-timeout 6 --confirm-timeout 3 --confirm-post-delay 1.0 --result-timeout 3 --close-result-dialog --result-close-pre-delay 0.5 --output <结果文件>.json
```

已验证通过的样例：

```powershell
python -m tdxquant.cli --exe-path D:\ProgramData\PinganSec\TdxW.exe --title-key "平安证券" pingan-buy-submit-once --port COM3 --hid-pre-delay 3 --code 516820 --price 0.35 --quantity 100 --post-delay 1.0 --max-depth 12 --dialog-timeout 6 --confirm-timeout 3 --confirm-post-delay 1.0 --result-timeout 3 --close-result-dialog --result-close-pre-delay 0.5 --output pingan-516820-submit-once-v4.json
```

### 6.3 连续下单判定标准

满足下面条件，才可认为本轮执行适合继续下一单：

- `confirm_click_wm_command = ok`
- `result_dialog_detected = ok`
- `result_dialog_focus_confirm = ok`
- `result_dialog_close = ok`
- `uia_after_confirm.data.root.enabled = true`

若最后一项不是 `true`，不要继续下一单。

当前最新验证结果：

- `pingan-buy-submit-once` 已达到连续下单可用标准
- 结果提示窗可自动关闭
- 主界面可自动恢复到下一单可执行状态
- 结果提示窗合同号已可自动提取，并回填到命令结果、状态文件与日志


## 7. 平安证券最终结论

当前版本平安证券的正式结论是：

- 已可实现自动买入闭环
- 已满足“不接受人工物理点击”的约束
- 但采用的是混合链路，不是纯后台消息链路

最终稳定策略：

- 填单：UIA
- 首次触发确认：HID `Tab + Enter`
- 推进买入确认：Win32 `WM_COMMAND`
- 关闭结果提示：先聚焦结果窗确认按钮，再 HID `Enter`

因此，平安证券现在可以作为当前项目的可用交易自动化实现。


## 8. 通达信最终结论

通达信当前版本的正式结论保持不变：

- 可探测
- 可填单
- 可触发提交按钮
- 可通过 `Stock` 注册消息切换主证券上下文
- 但证券代码输入仍未被交易业务层接受

因此：

- 通达信完整纯非物理下单链路未打通


## 9. 最终边界说明

### 已具备

- Windows 客户端路径发现
- Win32/UIA 控件树探测
- 平安证券完整自动买入闭环
- 结果提示窗自动关闭
- 平安证券结果窗合同号自动提取
- 固定状态文件 `runtime/pingan-last-order.json` 回填
- 连续下单前的主界面恢复判定
- 通达信主证券上下文切换验证

### 未具备

- 通达信完整纯非物理下单
- 通达信业务层认可的证券代码输入链路

### 当前建议归档状态

- 平安证券自动买入链路：完成
- 平安证券连续下单能力：完成
- 平安证券合同号自动提取：完成
- 通达信自动下单链路：未完成


## 10. 建议作为正式结论采纳的文本

建议项目内采用下面这段作为当前阶段正式结论：

> 当前版本平安证券客户端已验证打通自动买入闭环。实际可用实现采用 UIA 填单、HID 真实键盘触发首次确认、Win32 `WM_COMMAND` 推进买入确认，以及 HID `Enter` 关闭最终结果提示窗，命令执行完成后主界面可恢复到连续下单状态，并可从结果提示窗自动提取合同号，回填到命令 JSON、`runtime/pingan-last-order.json` 状态文件以及命令日志。当前版本通达信客户端仍未打通完整纯非物理下单链路，核心阻塞点仍是证券代码输入未被交易业务层接受。
