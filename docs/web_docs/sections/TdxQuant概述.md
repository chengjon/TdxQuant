# TdxQuant概述

## 步骤分解
> Source: https://help.tdx.com.cn/quant/docs/markdown/mindoc-1cfsjkbf8f3is/mindoc-1cv7o3nje2gu8.html

### 步骤分解

一个完整选股入自定义板块策略只需要两步:

### 第一步：客户端新增自定义板块

### 第二步：在VSCode里面运行以下python代码

实现运行函数：在这个策略里, 我们会根据运行结果做出相应操作:
```
# 策略说明：如果运行时间点价格高出昨收5%, 则进入涨幅选股板块，否则清空该板块
import pandas as pd
import numpy as np
from datetime import datetime
from tqcenter import tq

# 初始化tq
tq.initialize(__file__)

# 1. 基础配置
batch_codes = tq.get_stock_list_in_sector('通达信88') # 目标板块
start_time = "20251025" # 数据起始日期
target_end = datetime.now().strftime("%Y%m%d") # 数据结束日期（当前日期）
target_gain = 5.0 # 目标涨幅（%），可修改
target_block_name = 'ZFXG' # 目标自定义板块简称

# 2. 获取并整理收盘价数据
df_real = tq.get_market_data(
 field_list=['Close'],
 stock_list=batch_codes,
 start_time=start_time,
 end_time=target_end,
 dividend_type='front', # 前复权
 period='1d', # 日线
 fill_data=True # 填充缺失数据
)
# 转换为「日期×股票代码」的收盘价宽表
close_df = tq.price_df(df_real, 'Close', column_names=batch_codes)

# 3. 核心：计算当日相较于昨日的涨幅（%）
# 昨日收盘价（向下平移1行）
prev_close = close_df.shift(1)
# 计算涨幅：(当日收盘价 - 昨日收盘价) / 昨日收盘价 × 100%
daily_gain = (close_df - prev_close) / prev_close * 100

# 4. 筛选符合条件的股票（最新交易日涨幅超target_gain%）
latest_date = daily_gain.index[-1] # 最新交易日
latest_daily_gain = daily_gain.loc[latest_date] # 每只股票最新交易日的涨幅
# 筛选条件：涨幅 > target_gain%（排除NaN，避免数据异常）
target_stocks = latest_daily_gain[latest_daily_gain > target_gain].sort_values(ascending=False)
target_stocks_list = target_stocks.index.tolist() # 提取符合条件的股票代码列表

# 5. 结果输出与自定义板块操作（可按需注释）
print(f"\n=== 筛选结果（当日涨幅＞{target_gain}%）===")
if not target_stocks.empty:
 # ===================== 模块1：打印筛选结果 =====================
 print("【模块1：打印筛选结果】")
 print(f"符合条件的股票共 {len(target_stocks)} 只：")
 print(f"{'股票代码':<12} {'昨日收盘价':<12} {'当日收盘价':<12} {'当日涨幅':<10}")
 print("-" * 50)
 for stock_code, gain in target_stocks.items():
 prev_price = prev_close.loc[latest_date, stock_code]
 curr_price = close_df.loc[latest_date, stock_code]
 print(f"{stock_code:<12} {prev_price:<12.2f} {curr_price:<12.2f} {gain:<.2f}%")
 print("-" * 50)

 # ===================== 模块2：添加至自定义板块 =====================
 try:
 print("【模块2：自定义板块操作】")
 tq.send_user_block(block_code=target_block_name, stocks=target_stocks_list, show=True)
 print(f"✅ 已成功将股票添加至自定义板块「{target_block_name}」")
 except Exception as e:
 print(f"❌ 添加自定义板块失败：{e}")
 print("-" * 50)

else:
 # ===================== 模块1：打印空结果 =====================
 print("【模块1：打印筛选结果】")
 print(f"暂无当日涨幅＞{target_gain}%的股票")
 print("-" * 50)

 # ===================== 模块2：清空自定义选板块 =====================
 try:
 print("【模块2：自定义板块操作】")
 tq.send_user_block(block_code=target_block_name, stocks=[],show=True)
 print(f"✅ 已清空自定义板块「{target_block_name}」")
 except Exception as e:
 print(f"❌ 清空自定义板块失败：{e}")
 print("-" * 50)

```
### 结果示例

### VSCode端

### 通达信终端
---

## 安装Python及VSCode等开发环境
> Source: https://help.tdx.com.cn/quant/docs/markdown/mindoc-1cfsjkbf8f3is/mindoc-1d00970eq1rtc.html

### 安装Python及VSCode等开发环境

### 1.安装 Python 环境

安装Python：建议使用Python3.7及以上版本

### 1.1 下载地址：Python官网 (opens new window)

特别提示：安装时候务必勾选Add Python to PATH（将Python添加到环境变量）

### 2.安装IDE 建议VSCode、PyCharm或Trae

### 2.1 下载地址：Visual Studio Code官网 (opens new window)

### 2.2 安装 Python 插件（Extensions）

VSCode安装好后，在VSCode终端-扩展-输入下文，分别添加相关扩展：
-

简体中文
-

python

### 2.3 选择Python解释器：选择python3.13安装路径的exe
-

使用 Ctrl+Shift+P 快捷键打开 command palette 窗口
-

输入关键字 `python select` 并找到 `Python: Select Interpreter` 一项， 点击该项并在随后弹出的 Python 解释器列表中选择目标解释器：

### 2.4 在VSCode终端-扩展-分别输入下文，常用库建议安装：
- pip install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
- pip install pandas -i https://pypi.tuna.tsinghua.edu.cn/simple
- pip install backtrader -i https://pypi.tuna.tsinghua.edu.cn/simple
- pip install vectorbt -i https://pypi.tuna.tsinghua.edu.cn/simple

- 在 VSCode 中打开要调试的文件（如 tdxdemo.py）
- 在代码行号左侧单击，出现红点即表示断点已设置。
- 选择调试配置：点击左侧活动栏的“运行和调试”图标（或按 Ctrl+Shift+D),选择并启动调试配置（调试器类型选择 “Python Debugger” ）
- 自动生成配置：完成以上步骤后，VSCode会自动在项目根目录创建一个 .vscode 文件夹，并在里面生成 launch.json 文件.同时，调试下拉菜单就会出现，默认选中了“Python 文件”这个配置。
- 启动调试：按 F5 或点击绿色的“开始调试”按钮。

- 显示选择调试配置-“ Python文件 ”，调试打开的 Python 文件。
- 可以查看变量等等。

### 3.用户py的文件位置

在策略管理器界面，点击[文件位置]。

用户的py文件一般在客户端PYPlugins下面的user目录下面。py运行过程的生成的文件一般在PYPlugins下面的data和file目录下。
---

## 1. 安装通达信终端
> Source: https://help.tdx.com.cn/quant/docs/markdown/mindoc-1cfsjkbf8f3is/mindoc-1d00kk3jsibbc.html

### 1. 安装通达信终端

### 1.1 下载地址

内测版下载入口： 通达信金融终端内测版 (opens new window)

量化模拟下载入口： 金融终端(量化模拟) (opens new window)

正式版下载入口： 通达信金融终端、通达信专业研究版、期货通 (opens new window)

### 1.2 登录通达信客户端

### 1.3 系统-盘后数据下载

进行日线和分钟线等数据下载

### 2. 使用VSCode集成环境

### 2.1 使用VSCode运行py

### 2.1.1 打开py文件
- 在 VS Code 中点击打开一个本地文件夹，“文件”->"打开文件夹"。

### 2.1.2 运行py文件
- 在VSCode中打开通达信终端目录`.../PYPlugins/user`文件夹，运行tdxdata_test.py文件。

注意：客户端安装目录下面的`.../PYPlugins/user`文件夹中的`tqcenter.py`是最主要的TQData支撑文件，请勿修改或删除，否则需要重新下载。

### 2.2 使用VSCode编辑新文件

### 2.2.1 新建py文件

在打开的文件夹中鼠标右键创建新的".py" python 文件，文件名例如tdxdemo.py。

### 2.2.2 编辑py文件
```

# 使用tqcenter的API函数查看平安银行日线数据示例
from tqcenter import tq

#初始化
tq.initialize(__file__) #所有策略连接通达信客户端都必须调用此函数进行初始化

#获取平安银行日线前复权收盘数据
df = tq.get_market_data(
 field_list = ['Close'],
 stock_list = ["000001.SZ"],
 start_time = '20251219',
 end_time = '20251225',
 dividend_type='front',
 period='1d',
 )
print(df)

```
- 运行结果如图：
---
