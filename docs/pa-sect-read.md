# 证券公司客户端自动化交易实现指南

通过 Python + Windows API 实现后台自动下单，无需鼠标操作，窗口可最小化或运行于虚拟机中。

## 核心功能

- 最小化/虚拟机后台运行
- 无需鼠标操作，纯代码后台发送消息
- 自动查找窗口、控件句柄
- 自动填写股票代码、买入数量
- 自动点击下单按钮
- 前台办公不受干扰

---

## 原理说明

券商客户端均为原生 Win32 窗口，支持 Windows API 后台消息：

| API | 功能 |
|-----|------|
| `FindWindow` / `FindWindowEx` | 遍历窗口，查找控件句柄（最小化、虚拟机后台完全可用）|
| `WM_SETTEXT` | 后台给 Edit 输入框写文字，无需激活窗口、无需鼠标 |
| `BM_CLICK` | 后台给 Button 发送点击消息，无需鼠标点击 |

> **重点**：`SendMessage` 后台消息在最小化、后台、虚拟机、遮挡窗口等场景下全部生效，前台完全无感。

---

## 通用 Python 实现

### 安装依赖

```bash
pip install pywin32
```

### 完整代码

```python
import win32gui
import win32api
import win32con
import time

# ===================== 配置参数 =====================
券商窗口标题关键词 = "东方财富证券"  # 窗口标题里包含的字，不用完整
股票代码输入框类名 = "EDIT"
数量输入框类名 = "EDIT"
下单按钮类名 = "BUTTON"
买入股票代码 = "000001"
买入数量 = "100"
DELAY = 0.2  # 后台操作延迟
# ==================================================

def get_all_controls(hwnd_parent):
    """递归遍历后台所有子控件，返回所有句柄+类名+标题，最小化也能遍历"""
    controls = []
    def enum_child(hwnd, extra):
        class_name = win32gui.GetClassName(hwnd)
        window_text = win32gui.GetWindowText(hwnd)
        controls.append((hwnd, class_name, window_text))
        return True
    win32gui.EnumChildWindows(hwnd_parent, enum_child, None)
    return controls

# 1. 后台查找券商主窗口（最小化/虚拟机后台完全可找到）
main_hwnd = None
def find_main_window(hwnd, extra):
    title = win32gui.GetWindowText(hwnd)
    if 券商窗口标题关键词 in title:
        extra.append(hwnd)
    return True

win_list = []
win32gui.EnumWindows(find_main_window, win_list)
if not win_list:
    print("未找到券商窗口！")
    exit()
main_hwnd = win_list[0]
print(f"找到券商主窗口句柄: {main_hwnd}")

# 2. 后台递归查找所有Edit输入框、Button按钮
all_ctrl = get_all_controls(main_hwnd)

edit_code = None    # 股票代码输入框句柄
edit_num = None     # 数量输入框句柄
btn_order = None    # 下单按钮句柄

for hwnd, cls, txt in all_ctrl:
    if cls == "EDIT":
        if "代码" in txt or "证券代码" in txt:
            edit_code = hwnd
        if "数量" in txt or "股数" in txt:
            edit_num = hwnd
    if cls == "BUTTON" and ("买入" in txt or "下单" in txt):
        btn_order = hwnd

print(f"股票代码输入框: {edit_code}")
print(f"买入数量输入框: {edit_num}")
print(f"下单按钮: {btn_order}")

# 3. 后台写入内容【核心：最小化后台写入，不用点击输入框】
if edit_code:
    win32api.SendMessage(edit_code, win32con.WM_SETTEXT, 0, 买入股票代码)
if edit_num:
    win32api.SendMessage(edit_num, win32con.WM_SETTEXT, 0, 买入数量)

# 4. 后台点击下单按钮【核心：后台点击，不用鼠标、不用激活窗口】
if btn_order:
    win32api.SendMessage(btn_order, win32con.BM_CLICK, 0, 0)
    print("已后台发送下单点击指令")
```

---

## 平安证券专用代码

> 实测修正：本节下面这套“标准 MFC Win32 原生界面 + `WM_SETTEXT`/`BM_CLICK` 即可完成后台下单”的假设，不适用于当前实测的平安证券慧赢版本。当前版本虽然在买入区暴露了部分原生 UIA/Win32 控件，可用于填证券代码、价格、数量并读回联动状态，但最终提交按钮的纯非物理触发路径未打通。`invoke`、`BM_CLICK`、`WM_COMMAND`、`Enter` 都只能触发局部状态刷新，未进入确认/委托流程。
>
> 当前工程上可确认的能力边界是：
> - 可以做路径发现、窗口发现、UIA 探测
> - 可以做买入区填值与状态读回
> - 不应把“纯非物理最终提交”视为已实现

平安证券 PC 智投版 / 交易宝为标准 MFC Win32 原生界面，控件层级固定。

### 配置说明

- 窗口标题关键词：`平安证券`（智投版/交易宝通用）
- 需打开平安证券 PC → 登录 → 进入【普通买入委托】页面

### 完整代码

```python
import win32gui
import win32api
import win32con
import time

# ===================== 配置参数 =====================
WIN_TITLE_KEY = "平安证券"       # 窗口标题关键词
STOCK_CODE = "000001"            # 买入股票代码
BUY_AMOUNT = "100"               # 买入数量（必须100整数倍）
PRICE = "12.34"                  # 委托价格
DELAY = 0.2                      # 后台操作延迟
# ==================================================

def enum_all_child(hwnd_parent, ctrl_list):
    """递归遍历所有子控件（平安证券多层嵌套控件专用）"""
    def callback(hwnd, extra):
        cls = win32gui.GetClassName(hwnd)
        txt = win32gui.GetWindowText(hwnd)
        ctrl_list.append((hwnd, cls, txt))
        enum_all_child(hwnd, extra)  # 递归子控件
        return True
    win32gui.EnumChildWindows(hwnd_parent, callback, None)

def find_main_window():
    """后台查找平安证券主窗口"""
    def enum_win(hwnd, extra):
        title = win32gui.GetWindowText(hwnd)
        if WIN_TITLE_KEY in title:
            extra.append(hwnd)
        return True
    win_list = []
    win32gui.EnumWindows(enum_win, win_list)
    return win_list[0] if win_list else None

# ---------------------- 1. 查找主窗口 ----------------------
main_hwnd = find_main_window()
if not main_hwnd:
    print("❌ 未找到平安证券窗口！请先打开平安证券PC并登录，进入【买入委托】页面")
    exit()
print(f"✅ 找到平安证券主窗口句柄: {main_hwnd}")

# ---------------------- 2. 遍历所有控件 ----------------------
all_ctrl = []
enum_all_child(main_hwnd, all_ctrl)

# 匹配控件
hwnd_code = None     # 证券代码输入框
hwnd_price = None    # 委托价格输入框
hwnd_amount = None   # 买入数量输入框
hwnd_buy_btn = None  # 买入下单按钮

for hwnd, cls, txt in all_ctrl:
    if cls == "EDIT" and ("代码" in txt or "证券代码" in txt):
        hwnd_code = hwnd
    if cls == "EDIT" and ("价格" in txt or "委托价" in txt):
        hwnd_price = hwnd
    if cls == "EDIT" and ("数量" in txt or "股数" in txt):
        hwnd_amount = hwnd
    if cls == "BUTTON" and ("买入" in txt and "下单" not in txt):
        hwnd_buy_btn = hwnd

print(f"证券代码输入框: {hwnd_code}")
print(f"委托价格输入框: {hwnd_price}")
print(f"买入数量输入框: {hwnd_amount}")
print(f"买入下单按钮: {hwnd_buy_btn}")

if not all([hwnd_code, hwnd_amount, hwnd_buy_btn]):
    print("❌ 未找到买入页控件！请切换到【普通买入】委托页面")
    exit()

# ---------------------- 3. 后台写入内容 ----------------------
time.sleep(DELAY)
win32api.SendMessage(hwnd_code, win32con.WM_SETTEXT, 0, STOCK_CODE)
print(f"✅ 后台写入股票代码: {STOCK_CODE}")

time.sleep(DELAY)
if hwnd_price:
    win32api.SendMessage(hwnd_price, win32con.WM_SETTEXT, 0, PRICE)
    print(f"✅ 后台写入委托价格: {PRICE}")

time.sleep(DELAY)
win32api.SendMessage(hwnd_amount, win32con.WM_SETTEXT, 0, BUY_AMOUNT)
print(f"✅ 后台写入买入数量: {BUY_AMOUNT}")

# ---------------------- 4. 后台点击下单 ----------------------
time.sleep(DELAY)
win32api.SendMessage(hwnd_buy_btn, win32con.BM_CLICK, 0, 0)
print("✅ 已后台发送【买入下单】指令！")
```

---

## 注意事项

1. **窗口状态**：窗口可以最小化、最小化到托盘、放在虚拟机后台运行
2. **控件层级**：平安证券控件是多层嵌套子窗口，需使用递归遍历
3. **页面要求**：必须切换到【普通买入委托】页面，行情页无法找到控件
4. **运行方式**：可打包为 `.pyw` 文件实现无控制台静默运行

---

## 进阶功能

可扩展实现以下功能：

- 自动获取实时现价填入价格
- 自动查询可买数量、风控校验
- 下单后自动检测委托状态
- 定时循环盯盘、AI 信号自动下单
- 卖出、撤单全套功能

---

> ⚠️ **风险提示**：本代码仅供技术研究，请仔细甄别，谨慎投资。
