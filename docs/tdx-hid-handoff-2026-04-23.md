# 通达信 HID 线路暂停存档

日期：2026-04-23

## 1. 当前结论

- 平安证券线路已经收口为“探测、填单、读状态”能力。
- 在“不接受物理点击”的约束下，平安证券当前版本不作为最终下单方案。
- 通达信线路的 Win32/UIA 路线已经基本穷举。
- 当前唯一核心阻塞点仍然是：交易业务层不接受纯 Win32/UIA 写入的证券代码。
- 后续主路线已切换为 HID 硬件键盘模拟。


## 2. 已完成实现

### 2.1 文档

- [平安/通达信 Win32 联调总结](/opt/iflow/TdxQuant/docs/pingan-tdx-win32-validation-summary.md)
- [通达信 HID 硬件键盘模拟方案](/opt/iflow/TdxQuant/docs/tdx-hid-keyboard-plan.md)

### 2.2 代码

- [CLI 主入口](/opt/iflow/TdxQuant/tdxquant/cli.py)
- [Win32 能力层](/opt/iflow/TdxQuant/tdxquant/win32_api.py)
- [HID 串口桥接客户端](/opt/iflow/TdxQuant/tdxquant/hid_bridge.py)
- [Arduino HID 固件样例](/opt/iflow/TdxQuant/firmware/arduino/tdx_hid_keyboard/tdx_hid_keyboard.ino)

### 2.3 已新增命令

- `hid-ping`
- `hid-send`
- `tdx-hid-buy-probe`

### 2.4 测试结果

- `PYTHONPATH=. pytest -q tests/test_runtime.py tests/test_hid_bridge.py`
- 当前结果：`22 passed`

- `openspec validate implement-pingan-win32-trading-adapter --strict`
- 当前结果：通过


## 3. 当前 OpenSpec 状态

变更：

- `implement-pingan-win32-trading-adapter`

当前只剩两项未完成：

- `4.2` 在真实客户端上验证前台、最小化和遮挡场景，并记录控件识别差异
- `6.5` 在真实通达信上验证 HID 输入后，交易弹窗是否从“请输入证券代码!”推进到真正的下单确认

说明：

- `6.4` 已完成，代码层已经把通达信证券代码输入替换为 HID 真键盘输入。
- 剩余两项都依赖真实 Windows + 通达信 + HID 硬件环境，当前无法在 WSL 内完成。


## 4. 当前实现边界

### 4.1 已经具备的能力

- 通达信主窗口探测
- 通达信买入页关键句柄复用
- 前台窗口校验
- GUI 焦点校验
- 通过串口向 HID 设备发送：
  - `PING`
  - `KEY CTRL+A`
  - `KEY DELETE`
  - `TYPE 000001`
  - `TYPE 000001 TAB`
  - `TYPE 000001 ENTER`
- HID 输入后继续用 Win32 填价格、数量
- 继续用现有最优策略 `post_wm_command_parent` 触发提交
- 提交后等待并抓取潜在 UIA 弹窗

### 4.2 尚未验证的能力

- HID 输入后，通达信是否真正接受证券代码
- 是否需要 `TAB`
- 是否需要 `ENTER`
- 是否需要额外等待
- 提交后是否会进入真实确认框，而不是继续提示 `请输入证券代码!`


## 5. 后续恢复时的首要动作

拿到硬件后，按下面顺序恢复：

1. 在 Windows 端刷写固件：
   - [tdx_hid_keyboard.ino](/opt/iflow/TdxQuant/firmware/arduino/tdx_hid_keyboard/tdx_hid_keyboard.ino)
2. 确认设备串口号，例如 `COM3`
3. 在 Windows 项目目录安装依赖：
   - `pip install -r requirements.txt`
4. 先跑链路自检：
   - `python -m tdxquant.cli hid-ping --port COM3`
5. 再跑单条输入测试：
   - `python -m tdxquant.cli hid-send --port COM3 --wire-command "TYPE 000001 TAB"`
6. 最后跑完整半闭环：
   - `python -m tdxquant.cli --title-key 通达信金融终端 tdx-hid-buy-probe --window-key 通达信金融终端 --port COM3 --code 000001 --price 10.00 --quantity 100 --pre-clear --commit-key tab --submit-strategy post_wm_command_parent --output tdx-hid-buy-probe.json`


## 6. 恢复时的建议验证顺序

建议按三轮做，不要直接跑完整下单链路。

第一轮：

- 只验证 `hid-ping`
- 只验证 `hid-send`
- 确认设备协议无误

第二轮：

- 打开通达信买入页
- 只做代码输入验证
- 比较 `TYPE 000001`
- 比较 `TYPE 000001 TAB`
- 比较 `TYPE 000001 ENTER`

第三轮：

- 使用 `tdx-hid-buy-probe`
- 价格继续使用明显不能成交的低价
- 观察弹窗是否越过 `请输入证券代码!`


## 7. 关键注意事项

- `--title-key` 是全局参数，必须放在子命令前。
- `hid-send` 使用的是 `--wire-command`，不是 `--command`。
- 当前实现默认假设通达信买入页关键句柄仍与此前抓取一致；如果通达信版本变化，可能要先重做句柄探测。
- 当前阶段不要把 HID 设备做成通用宏键盘，协议面必须保持最小化。
- 当前阶段仍然要坚持“低价不成交验证”，不要直接做可成交价格测试。


## 8. 一句话恢复点

下次恢复时，不需要再重做 Win32/UIA 穷举；直接从“HID 硬件到位后，跑 `hid-ping` -> `hid-send` -> `tdx-hid-buy-probe`”这一条线继续。
