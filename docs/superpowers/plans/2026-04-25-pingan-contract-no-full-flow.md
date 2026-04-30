# PingAn 合同号自动提取全流程记录

## 1. 目标

本次工作的目标是把 `pingan-buy-submit-once` 收口到可正式使用状态，满足下面 4 项：

- 自动完成平安证券买入下单
- 自动推进确认
- 自动关闭结果窗
- 命令执行完成后主界面恢复，可继续下一单

在这个基础上，继续补齐“合同号自动提取”能力，并把合同号同时回填到：

- 命令结果 JSON
- 固定状态文件 `runtime/pingan-last-order.json`
- 命令日志

## 2. 初始状态

一开始已经确认的能力边界是：

- `pingan-buy-submit-once` 已能完成自动下单、确认推进、关闭结果窗
- 主界面在命令结束后能恢复到可继续下一单的状态
- 合同号自动提取在文档中仍标记为“待后续增强”

最早定位到的现有提取逻辑在 `tdxquant/uia_inspector.py`，函数是 `_extract_dialog_text_payload()`，它只做了非常轻量的 Win32 子控件文本扫描。

## 3. 第一阶段排查结论

### 3.1 先确认不是流程问题

先检查了 `pingan-buy-submit-once` 的实现链路，确认它已经在做下面几件事：

- 下单前 UIA 填值
- 通过 HID `Tab + Enter` 进入确认
- 通过 Win32 `WM_COMMAND` 推进确认
- 找到结果窗后通过 HID `Enter` 关闭

所以“合同号拿不到”一开始被限定为“结果窗读取问题”，不是下单链路问题。

### 3.2 先完成回填框架

在还没稳定提取合同号之前，先把回填基础设施补齐：

- `tdxquant/cli.py` 中新增固定状态文件路径 `runtime/pingan-last-order.json`
- `pingan-buy-submit-once` 执行后，无论是否提取成功，都先写状态文件
- 命令结果 JSON 中增加 `data.artifacts.last_order_state_path`
- stderr 增加 `contract_no` 输出

这样后续即使提取失败，仍然能从统一的输出位置继续诊断。

## 4. 第一轮失败与根因收敛

第一次在真实运行目录里读结果文件时，发现：

- `data.result_dialog.contract_no = null`
- `runtime/pingan-last-order.json` 也存在，但 `contract_no = null`
- `artifacts.last_order_state_path` 一开始甚至不存在

这一步暴露出一个关键事实：用户实际运行的目录不是当前工作区 `/opt/iflow/TdxQuant`，而是 `/mnt/d/MyCode3/tdx`。

对应证据：

- `/mnt/d/MyCode3/tdx/tdxquant/cli.py` 里没有新增的回填逻辑
- `/opt/iflow/TdxQuant/tdxquant/cli.py` 里已经有新逻辑

结论：

- 第一次真实执行跑的是旧代码副本
- 不是新实现失效，而是运行目录没有同步

处理动作：

- 把 `cli.py`
- `uia_inspector.py`
- `tests/test_runtime.py`
- `README.md`

从当前工作区同步到 `/mnt/d/MyCode3/tdx`

## 5. 第二轮失败与诊断增强

同步后再次运行，发现：

- `artifacts.last_order_state_path` 已经出现
- `runtime/pingan-last-order.json` 已经生成
- 但 `contract_no` 仍然是 `null`

同时结果窗采样内容显示为空：

- `win32_child_texts = []`
- `uia_texts = []`
- `merged_texts = []`

这一步不能再猜正则或文案，需要先确认“正文到底有没有被读取到”。

因此新增了两类诊断信息：

### 5.1 Win32 深层文本诊断

新增 `win32_descendant_texts`，递归枚举结果窗后代 Win32 子控件，并记录：

- `hwnd`
- `parent_hwnd`
- `depth`
- `class_name`
- `text`

### 5.2 UIA 局部子树诊断

新增 `uia_tree`，把结果窗本身的局部 UIA 子树序列化到结果 JSON。

目的不是直接修，而是先回答两个问题：

- 结果窗正文是不是在更深层的 Win32 控件里
- 结果窗正文是不是 UIA 能看到、只是当前选择器没覆盖到

## 6. 第二轮诊断结果

加入诊断增强后再运行，得到两个非常明确的根因。

### 6.1 实际正文已经被读到

在 `steps.result_dialog_detected.result.data` 中可以读到：

`委托已提交,合同号是0362577001`

也就是说，问题不是“结果窗正文读不到”，而是“已经读到，但没被正确提取”。

### 6.2 真实失败点有两个

第一个失败点：

- 原正则只匹配 `合同号:` / `合同号：`
- 实际客户端文案是 `合同号是0362577001`

第二个失败点：

- `steps.result_dialog_detected.result.data` 保存的是关闭前快照
- 但最终顶层 `data.result_dialog` 又重新基于 `result_dialog["element"]` 取了一次
- 结果窗被关闭后，这个 UIA 元素退化成了空 `Pane`
- 所以最终结果 JSON 顶层又被空数据覆盖

换句话说：

- 中间步骤里已经拿到了有效正文
- 最终输出时又被“关闭后的空窗口快照”覆盖掉了

## 7. 最终修复

### 7.1 放宽合同号正则

把合同号提取规则从仅支持：

- `合同号:`
- `合同号：`

扩展为同时支持：

- `合同号是`
- `合同号 :`
- `合同号：`

对应实现位于：

- `tdxquant/uia_inspector.py`
- `_extract_contract_no_from_texts()`

### 7.2 保留关闭前的结果窗快照

在 `run_pingan_buy_submit_once()` 中：

- 先把 `result_dialog_detected` 的有效快照保存到 `detected_result_dialog_data`
- 最终返回时，顶层 `data.result_dialog` 直接复用这个关闭前快照
- 不再在结果窗关闭后重新读取一次 UIA 元素

这样最终 JSON 中保留下来的就是“真正有正文的那一份”

### 7.3 保留诊断信息

最终版本保留了以下调试字段，便于以后再次排障：

- `win32_child_texts`
- `win32_descendant_texts`
- `uia_texts`
- `uia_tree`
- `merged_texts`

这些字段即使以后再次出现合同号提取异常，也能直接用来判断究竟是：

- 文案格式变了
- Win32 结构变了
- UIA 行为变了
- 还是关闭时机覆盖了结果

## 8. 最终验收结果

最后一次实机运行，已经确认：

- 结果 JSON 中：
  - `data.result_dialog.contract_no = "0361818001"`
- 状态文件中：
  - `contract_no = "0361818001"`
- 结果 JSON 中：
  - `data.artifacts.last_order_state_path = "runtime\\pingan-last-order.json"`

结果窗正文也被稳定抓到：

- `委托已提交,合同号是0361818001`

所以本次能力已经正式闭环完成：

- 自动下单：完成
- 自动推进确认：完成
- 自动关闭结果窗：完成
- 主界面恢复可继续下一单：完成
- 合同号自动提取：完成
- 命令结果 JSON 回填：完成
- 固定状态文件回填：完成
- 日志回填：完成

## 9. 这次实际修改过的关键文件

代码：

- `tdxquant/cli.py`
- `tdxquant/uia_inspector.py`
- `tests/test_runtime.py`

文档：

- `README.md`
- `docs/pingan-tdx-win32-validation-summary.md`

运行目录同步副本：

- `/mnt/d/MyCode3/tdx/tdxquant/cli.py`
- `/mnt/d/MyCode3/tdx/tdxquant/uia_inspector.py`
- `/mnt/d/MyCode3/tdx/tests/test_runtime.py`
- `/mnt/d/MyCode3/tdx/README.md`
- `/mnt/d/MyCode3/tdx/docs/pingan-tdx-win32-validation-summary.md`

## 10. 以后如果再出问题，优先按这个顺序查

### 10.1 先确认运行目录是不是最新代码

不要先怀疑功能坏了，先确认实际执行目录是否就是最新副本。

本次就出现过一次典型误判：

- 工作区里代码已改好
- 但 Windows 实际运行目录还是旧版本

第一检查项：

- 实际执行目录中的 `tdxquant/cli.py`
- 实际执行目录中的 `tdxquant/uia_inspector.py`

是否已经包含：

- `PINGAN_LAST_ORDER_STATE_PATH`
- `last_order_state_path`
- `win32_descendant_texts`
- `uia_tree`

### 10.2 看顶层结果，不要只看命令退出码

优先检查这两个文件：

- `pingan-submit-once-result.json`
- `runtime/pingan-last-order.json`

关键字段：

- `data.result_dialog.contract_no`
- `data.result_dialog.merged_texts`
- `data.result_dialog.win32_descendant_texts`
- `data.result_dialog.uia_tree`
- `data.artifacts.last_order_state_path`
- `contract_no`

### 10.3 如果 `contract_no = null`

先看 `merged_texts`：

- 如果 `merged_texts` 里已经有 `合同号...`，说明是正则问题
- 如果 `merged_texts` 为空，但 `win32_descendant_texts` 有正文，说明合并逻辑有问题
- 如果 `win32_descendant_texts` 和 `uia_tree` 都没有正文，说明结果窗结构或控件读取行为变了

### 10.4 如果中间步骤有正文、顶层结果却为空

优先怀疑“关闭后快照覆盖”类问题。

本次就属于这个问题：

- `steps.result_dialog_detected.result.data` 已有正文
- 顶层 `data.result_dialog` 却变成空 `Pane`

处理原则：

- 最终输出优先复用关闭前有效快照
- 不要用关闭后的 UIA 元素重新取值覆盖结果

## 11. 推荐保留的验收方式

每次发版或迁移运行目录后，建议至少做一次实单或准实单验收，并核对：

- stderr 是否打印 `contract_no`
- `pingan-submit-once-result.json` 中是否有 `data.result_dialog.contract_no`
- `runtime/pingan-last-order.json` 中是否有 `contract_no`
- 三处合同号是否一致
- 结果窗关闭后是否还能继续下一单

## 12. 本文档用途

本文档用于以后两种场景：

- 新环境迁移后，快速确认这套能力是怎么打通的
- 未来如果合同号再次提取失败，按本文的排查顺序快速定位是“运行目录问题、读取问题、正则问题，还是关闭后覆盖问题”

## 13. 后续性能优化记录

在合同号自动提取闭环完成后，又继续对 `pingan-buy-submit-once` / `pingan-buy` 的执行耗时做了专项优化。

### 13.1 初始问题

虽然自动下单链路已经可用，但整体耗时明显长于人工操作。

因此新增了两件事：

- 新增高层命令 `pingan-buy`
- 在结果 JSON 中新增 `timing.total_ms` 和 `timing.steps`

这样后续优化不再靠感觉，而是可以直接看每一步耗时。

### 13.2 高层命令与 profile

新增的高层命令是：

- `pingan-buy`

它的设计目标是：

- 固定自动下单闭环流程
- 只暴露常用业务参数
- 通过 profile 管理延时参数

当前支持的 profile：

- `stable`
- `balanced`
- `fast`
- `turbo`

默认推荐：

- `balanced`

如果要直接使用当前已验证的极速组合，现在也可以直接用：

- `turbo`

它等价于：

- `--price-quantity-input-mode hybrid_win32`
- `--dialog-lookup-mode win32_experimental`

### 13.3 第一次耗时采样

在高层命令刚落地、但底层仍复用探测型链路时，采样结果是：

- 总耗时约 `70.15s`

时间主要花在：

- `submit_probe` 约 `57.73s`

这说明最大问题不是确认框或结果窗等待，而是生产命令仍在复用一条“诊断型/探测型”路径。

### 13.4 第一次结构优化

做法：

- 保留 `pingan-buy-submit-once` 作为诊断命令
- 新增真正的生产快路径 `run_pingan_buy_fast()`
- `pingan-buy` 改走生产快路径
- 去掉生产路径里的大量探测动作

移除或默认关闭的重操作包括：

- `windows_before`
- 多个 `read_*_before/after`
- `dialogs_after`
- 默认最终 UIA 全树抓取

结果：

- 总耗时从 `70.15s` 降到 `30.94s`

### 13.5 第二次优化：窗口缓存

做法：

- 快路径中只查一次主窗口
- 后续输入动作复用同一个窗口对象
- 减少每一步重新从桌面枚举窗口的成本

结果：

- 总耗时从 `30.94s` 降到 `28.93s`

### 13.6 第三次实验：Win32 输入

实验目标：

- 尝试把 `code / price / quantity` 三个输入从 UIA 写值切到 Win32 `WM_SETTEXT`

实验中验证出的事实：

- Win32 写值本身很快
- 但为了拿 Win32 句柄而引入的 `detect()` 过程极重
- 在当前客户端版本下，Win32 写值还不稳定影响后续确认链路

实测结果：

- `win32_handle_detect` 单步耗时达到约 `350s`
- 整体命令失败，未进入确认框

结论：

- Win32 输入实验不适合作为当前生产路径
- 已撤回该实验逻辑

### 13.7 第四次优化：UIA 定点查找 + 缓存

在撤回 Win32 输入实验后，保留 UIA 输入语义，但继续优化查找方式：

- 优先按 `automation_id` 直接查找控件
- 仅在直查失败时回退到窗口内遍历
- 对已找到的控件进行缓存复用

当前关键控件：

- `12005` 证券代码输入框
- `12006` 价格输入框
- `12007` 数量输入框

最终结果：

- 总耗时从 `28.93s` 降到 `27.83s`
- 同时保持下单成功
- 合同号提取和状态文件回填保持正常

### 13.8 当前阶段的最终性能结论

截至本文更新时，几次版本对比如下：

- 探测型高层命令：约 `70.15s`
- 第一版快路径：约 `30.94s`
- 窗口缓存版：约 `28.93s`
- UIA 定点查找 + 缓存版：约 `27.83s`

也就是说，目前已经把整条链路从约 `70s` 压到约 `28s`。

### 13.9 当前剩余瓶颈

从最新 `timing.steps` 看，主要耗时仍集中在：

- `set_code`
- `set_price`
- `set_quantity`
- `focus_quantity_input`
- `confirm_lookup`
- `result_dialog_lookup`

这说明当前剩余瓶颈已经不是“整体流程设计错误”，而是：

- pywinauto / UIA 本身的交互成本
- UIA 输入和聚焦动作本身偏慢
- 确认框、结果窗查找轮询仍偏保守

### 13.10 下一阶段更激进实验建议

如果还要继续提速，下一步就应进入更激进的实验阶段，建议顺序如下：

1. 进一步减少 UIA 写值次数
2. 对价格/数量分别实验更轻的输入策略
3. 研究确认框/结果窗更直接的定位路径
4. 尝试复用 HID 串口连接，减少重复开关串口成本

注意：

- 这类实验必须继续保留 `timing` 打点
- 生产可用路径和实验路径必须分开
- 任何实验都不能破坏当前已验证完成的合同号提取与结果窗关闭链路

### 13.11 当前已落地的受控实验开关

为了把“流程固定”和“参数灵活”同时保留下来，`pingan-buy` 继续维持高层封装，但新增了一个更细粒度的实验参数：

- `--price-quantity-input-mode uia|win32|hybrid_win32`
- `--dialog-lookup-mode uia|win32_experimental`

设计边界如下：

- `code` 继续固定走 UIA 写值，不参与本轮激进实验
- `price` / `quantity` 才允许切换输入模式
- 默认仍然是 `uia`，保证生产路径不因实验自动漂移

三种模式的含义：

- `uia`：价格和数量继续走当前稳定 UIA 写值路径
- `win32`：价格和数量只走缓存句柄上的 Win32 `WM_SETTEXT`
- `hybrid_win32`：先尝试缓存句柄 Win32 写值，再做回读校验；如果句柄不可用或回读不一致，则自动回退到 UIA

`dialog_lookup_mode` 的边界如下：

- `uia`：继续走当前稳定的确认框/结果窗 UIA 查找路径
- `win32_experimental`：先尝试用 Win32 顶层窗口枚举定位 `买入交易确认` / `提示` 这两个 `#32770` 窗口，再找对应子按钮

这里明确把它做成实验开关，而不是直接替换生产路径，原因是：

- 这类优化的收益和风险都集中在弹窗阶段
- 一旦判断条件稍有偏差，就可能卡在“买入确认”窗口
- 因此实验模式必须允许独立开启，并在失败时自动回退到稳定 UIA 路径

这里选择 `hybrid_win32` 而不是直接替换生产路径，原因是：

- 上一轮全量 Win32 实验已经证明“句柄探测”成本过高
- 当前实验只允许复用已经找到的 UIA 缓存句柄，不能重新引入 `detect()`
- 价格/数量的业务风险明显低于代码输入，所以先从这两个控件切入

### 13.12 本轮预期收益

这轮实验主要想回答两个问题：

1. 价格/数量写值是否能明显快于 UIA `set_edit_text()`
2. `focus_quantity_input` 改为复用缓存控件后，是否能消掉一次窗口内全树遍历

如果实测有效，理论上最先应下降的步骤是：

- `set_price`
- `set_quantity`
- `focus_quantity_input`

如果这三步下降明显，而 `confirm_lookup` / `result_dialog_lookup` 仍然偏大，那么下一阶段就应集中优化弹窗定位，而不是继续折腾输入框。
