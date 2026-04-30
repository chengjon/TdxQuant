 通达信量化平台

TdxQuant 简介

TdxQuant是由深圳市财富趋势科技股份有限公司研发的专业量化投研平台，专注于为国内量化投资者提供从策略研究到投资决策

的全流程解决方案。平台以高效、简洁为核心设计理念，致力于降低量化交易门槛，提升策略开发与执行的效率。

依托通达信近三十余年在金融科技领域的深厚积累，TdxQuant集成了完备的实时和历史行情数据、金融数据库及稳定的交易系统

基础设施，为策略的研发、回测、验证和执行提供了坚实可靠的技术支持。

平台采用分层化、模块化的服务体系，可灵活适配从高校学生、独立研究者、个人投资者到专业机构等不同用户的需求，实现从

策略构思到交易落地的无缝衔接。

TdxQuant 服务介绍

TdxQuant 是一套基于通达信金融终端构建的 Python 量化策略运行框架。该框架通过 API 接口形式，为策略交易提供所需的行情

数据获取与交易指令执行功能。

运行环境要求

TdxQuant 支持 64 位 Python 3.7、3.8、3.9、3.10、3.11、3.12、3.13等版本，系统会自动适配当前 Python 版本，建议使用3.13

版本。

请注意：运行 TdxQuant 程序前，需预先启动支持TQ策略功能的 通达信金融终端、专业研究版等版本。

核心运行逻辑

TdxQuant 以 tqcenter 行情模块为核心，专注于为量化交易者提供高效、直接的数据服务，主要包含以下内容：

行情数据：实时与历史的快照、K 线、分笔（Tick）数据

基本面数据：除权除息、基本财务、专业财务、股票交易数据、市场数据等

新股和合约等信息：标的基础信息、可转债、新股申购等

分类数据：市场类型、行业分类、自定义板块等

核心应用场景

TdxQuant提供覆盖量化投研全流程的核心功能模块，主要应用场景包括：

1. 策略研发与历史回测

平台提供“即用型”标准化数据。所有历史与实时数据均在服务端完成清洗、对齐，并预加载至客户端。支持用户快速获取指定时

间维度的历史数据，并进行策略信号计算与回测分析。既提供复权因子，也提供各种类型的复权后的数据。

2. 实时监控与信号预警

支持实时行情数据订阅，用户可基于自定义的指标与因子模型进行在线计算。当预设条件触发时，系统通过信号接口实时推送预

警信息至客户端，助力研究者及时捕捉市场动态与交易机会。

3. 交易模拟与实盘执行

平台构建了完整的策略交易闭环，提供模拟交易、券商实盘等两种执行环境：

模拟交易：在仿真市场环境中，使用实时行情数据对策略进行持续跟踪与验证，评估其实际表现，全程无资金风险。

实盘交易：通过稳定的交易总线，安全对接券商报盘系统，实现策略信号的自动化、高可靠性下单与交易管理。

 通达信量化平台

量化交易的核心价值

1. 利用历史数据高效验证策略，提升研究效率数百倍

在验证交易策略时，历史回测是评估其有效性的关键环节，但传统人工方式难以处理海量数据与复杂计算。量化交易可在几分钟

内完成一次全面回测，快速获得统计验证结果，极大提升了策略研发的迭代效率。

2. 实时捕捉基于概率的获胜机会

量化交易借助计算机强大的数据处理能力，能够从海量市场信息中发掘人工难以察觉的规律与机会。面对全市场数千只股票的实

时波动，量化系统可同时监控多重条件，避免机会错失。它能够综合考量选股、择时、资产配置与风险管理，构建并执行具有较

大概率的投资组合，追求收益最大化。

3. 实现科学、客观的投资决策

与传统主观投资不同，量化交易将投资理念、经验甚至市场直觉转化为严谨的数学模型。通过系统化的信号生成与执行机制，有

效克服人性中的情绪偏差，使投资决策过程更具纪律性、可重复性与可优化性。

量化交易的工具挑战

工欲善其事，必先利其器。 对于个人投资者而言，独立搭建一套完整的量化交易体系，复杂繁琐，涉及数据、系统、策略等多

层面的巨大投入。

一、需要准确、全面的金融数据基础

量化交易依赖于高质量的历史与实时数据，包括行情、财务、宏观及基本面数据等。构建和维护这样一个数据仓库，不仅需要持

续的数据采购、清洗、更新与运维成本，还需在数据存储、访问速度与系统稳定性方面进行深入的技术投入。

二、需要易用、可靠的量化交易系统

一个成熟的量化平台需要支持多样的策略开发语言、具备高速的回测与模拟引擎、提供科学的策略评估体系，并为实盘交易提供

全方位的保障。过往，研究者往往需要兼具复杂的金融数据知识与工程构建能力。如今，TdxQuant让您只需专注于策略逻辑本

身，其余复杂工作交给平台。

TdxQuant的核心优势

TdxQuant是一款集金融数据与策略投研工具于一体的量化平台，结构清晰，简洁易上手，数据获取快捷，算法资源丰富。我们的

目标是为投资者提供"开箱即用"的完整解决方案。

1. 全方位保障策略安全与自主

支持策略在本地IDE环境中开发与运行，保障代码安全与私密性

分离式模块化架构，策略的编码和调试更加自由和灵活

2. 大幅降低量化交易门槛

提供高质量、高精度、快速接入的金融元数据

支持多种策略类型的便捷编写、回测、模拟与实盘

3. 助力构建专业量化成长路径

通过"投资学院"系统学习量化交易相关知识体系

 通达信量化平台

通过"宽客社区"交流心得、解答疑惑

全程助力用户从入门到精通，成为专业的量化投资者

 通达信量化平台

📋 更新日志

📅 2026-02-28 更新说明

问题修复：修复了formula_process_mul_zb等入参retrun_count拼写错误问题

更新函数：get_more_info，get_cb_info，get_market_snapshot加上了字段筛选功能

更新函数：get_more_info等支持更多行情数据项，输出顺序进行归整

其他修正：tqcenter几处细节修改

📅 2026-02-12 更新说明

更新函数：send_user_block可以添加股票进自选股，自选股简称为ZXG

其他更新：批量调用公式内部优化提速

其他更新：新增港股指数（.HI）

其他更新：解决多个客户端同时运行时的TQ冲突的问题

📅 2026-02-07 更新说明

新增函数：批量调用选股公式formula_process_mul_xg

新增函数：批量调用指标公式formula_process_mul_zb

更新函数：get_stock_list、 get_sector_list、 get_stock_list_in_sector新增参数list_type，可以选择返回股票名称

更新函数：tdx_formula返回做出修改，条件选股和专家选股只返回'1'和'0'

更新函数：formula_zb新增参数xsflag，可以设置返回数据的小数位数

更新函数：download_file新增下载：最近舆情、综合信息文件

更新函数：get_stock_info新增部分数据字段输出

📅 2026-01-31 更新说明

新增功能：支持调用通达信公式进行计算

新增函数：格式化K线数据formula_format_data

新增函数：向通达信公式系统设置数据formula_set_data

新增函数：向通达信公式系统设置数据信息formula_set_data_info

新增函数：获取公式中的设置数据formula_get_data

新增函数：调用通达信技术指标公式formula_zb

新增函数：调用通达信条件选股公式formula_xg

新增函数：调用通达信专家系统公式formula_exp

新增函数：获取股票更多信息get_more_info

新增函数：获取每天的股本数据get_gb_info

更新函数：刷新行情缓存refresh_cache，新增参数force和market，可指定强制刷新或指定市场刷新

其他更新：新增中证指数（.CSI），中金所期货（.CFF），宏观数据（.HG）等市场后缀识别和数据获取

其他更新：获取非指定日期的股票交易数据，板块交易数据等数据时增加了对应日期返回。

问题修复：修复了部分市场数据返回时小数位数不对导致的精度问题。

问题修复：修复了获取Python3.9以及之前版本依赖库错误问题。

📅 2026-01-17 正式发布

安装Python及开发环境 →

 通达信量化平台

安装Python及VSCode等开发环境

1.安装 Python 环境

安装Python：建议使用Python3.7及以上版本

1.1 下载地址：Python官网

特别提示：安装时候务必勾选Add Python to PATH（将Python添加到环境变量）

2.安装IDE 建议使用VSCode或PyCharm

2.1 下载地址：Visual Studio Code官网

2.2 安装 Python 插件（Extensions）

VSCode安装好后，在VSCode终端-扩展-输入下文，分别添加相关扩展：

简体中文

python

 通达信量化平台

2.3 选择Python解释器：选择python3.13安装路径的exe

使用 Ctrl+Shift+P 快捷键打开 command palette 窗口

输入关键字  python select  并找到  Python: Select Interpreter  一项， 点击该项并在随后弹出的 Python 解释器列表中选

择目标解释器：

2.4 在VSCode终端-扩展-分别输入下文，常用库建议安装：

pip install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple

pip install pandas -i https://pypi.tuna.tsinghua.edu.cn/simple

pip install backtrader -i https://pypi.tuna.tsinghua.edu.cn/simple

pip install vectorbt -i https://pypi.tuna.tsinghua.edu.cn/simple

 通达信量化平台

在 VSCode 中打开要调试的文件（如 tdxdemo.py）

在代码行号左侧单击，出现红点即表示断点已设置。

选择调试配置：点击左侧活动栏的“运行和调试”图标（或按 Ctrl+Shift+D),选择并启动调试配置（调试器类型选择 “Python

Debugger” ）

自动生成配置：完成以上步骤后，VSCode会自动在项目根目录创建一个 .vscode 文件夹，并在里面生成 launch.json 文件.同

时，调试下拉菜单就会出现，默认选中了“Python 文件”这个配置。

启动调试：按 F5 或点击绿色的“开始调试”按钮。

显示选择调试配置-“ Python文件 ”，调试打开的 Python 文件。

可以查看变量等等。

 通达信量化平台

3.用户py的文件位置

在策略管理器界面，点击[文件位置]。

用户的py文件一般在客户端PYPlugins下面的user目录下面。py运行过程的生成的文件一般在PYPlugins下面的data和file目录下。

← 版本更新说明

安装通达信终端并获取数据 →

 通达信量化平台

1. 安装通达信终端

1.1 下载地址

内测版下载入口： 通达信金融终端内测版

正式版下载入口： 通达信金融终端64位版、通达信专业研究版

1.2 登录通达信金融终端

1.3 系统-盘后数据下载

进行日线和分钟线等数据下载

 通达信量化平台

2. 使用VSCode集成环境

2.1 使用VSCode运行py

2.1.1 打开py文件

在 VS Code 中点击打开一个本地文件夹，“文件”->"打开文件夹"。

2.1.2 运行py文件

在VSCode中打开通达信终端目录 .../PYPlugins/user 文件夹，运行tdxdata_test.py文件。

 通达信量化平台

注意：客户端安装目录下面的 .../PYPlugins/user 文件夹中的 tqcenter.py 是最主要的TQData支撑文件，请勿修改或删除，否

则需要重新下载。

2.2 使用VSCode编辑新文件

2.2.1 新建py文件

在打开的文件夹中鼠标右键创建新的".py" python 文件，文件名例如tdxdemo.py。

2.2.2 编辑py文件

1

2

3

# 使用tqcenter的API函数查看平安银行日线数据示例

from tqcenter import tq

py

4

 通达信量化平台
#初始化

5

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

6

7

8

9

10

11

12

13

14

15

16

17

18

运行结果如图：

← 安装Python及开发环境

快速开始第一个策略 →

 通达信量化平台

步骤分解

一个完整选股入自定义板块策略只需要两步:

第一步：客户端新增自定义板块

第二步：在VSCode里面运行以下python代码

实现运行函数：在这个策略里, 我们会根据运行结果做出相应操作:

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

# 策略说明：如果运行时间点价格高出昨收5%, 则进入涨幅选股板块，否则清空该板块

py

import pandas as pd

import numpy as np

from datetime import datetime

from tqcenter import tq

# 初始化tq

tq.initialize(__file__)

# 1. 基础配置

batch_codes = tq.get_stock_list_in_sector('通达信88')     # 目标板块

start_time = "20251025"                                  # 数据起始日期

target_end = datetime.now().strftime("%Y%m%d")           # 数据结束日期（当前日期）

target_gain = 5.0                                        # 目标涨幅（%），可修改

target_block_name = 'ZFXG'                               # 目标自定义板块简称

# 2. 获取并整理收盘价数据

df_real = tq.get_market_data(

    field_list=['Close'],

    stock_list=batch_codes,

    start_time=start_time,

    end_time=target_end,

23

    dividend_type='front',  # 前复权

 通达信量化平台

24

    period='1d',            # 日线

    fill_data=True          # 填充缺失数据

)

# 转换为「日期×股票代码」的收盘价宽表

close_df = tq.price_df(df_real, 'Close', column_names=batch_codes)

# 3. 核心：计算当日相较于昨日的涨幅（%）

# 昨日收盘价（向下平移1行）

prev_close = close_df.shift(1)

# 计算涨幅：(当日收盘价 - 昨日收盘价) / 昨日收盘价 × 100%

daily_gain = (close_df - prev_close) / prev_close * 100

# 4. 筛选符合条件的股票（最新交易日涨幅超target_gain%）

latest_date = daily_gain.index[-1]              # 最新交易日

latest_daily_gain = daily_gain.loc[latest_date] # 每只股票最新交易日的涨幅

# 筛选条件：涨幅 > target_gain%（排除NaN，避免数据异常）

target_stocks = latest_daily_gain[latest_daily_gain > target_gain].sort_values(ascending=False)

target_stocks_list = target_stocks.index.tolist()  # 提取符合条件的股票代码列表

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

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

53

54

55

56

57

58

59

60

61

62

63

64

65

66

67

68

69

70

71

72

73

74

75

76

77

78

79

80

81

82

83

 通达信量化平台

结果示例

VSCode端

通达信终端

← 安装通达信终端并获取数据

初始化initialize →

 通达信量化平台

初始化initialize

1

initialize(__file__) #所有策略连接通达信客户端都必须调用此函数进行初始化

调用方法:

1

2

3

from tqcenter import tq

tq.initialize(__file__)

注意事项:

1."initialize"不可修改。

2.该函数用于初始化，任何一个策略都必须有该函数。

py

py

← 快速开始第一个策略

订阅行情subscribe_hq →

py

py

 通达信量化平台

订阅行情subscribe_hq

订阅股票实时更新

1

subscribe_hq(stock_list: List[str] = [],callback = None):

输入参数

参数

stock_list

callback

是否必选

参数类型

参数说明

Y

Y

List[str]

订阅的证券代码

str

回调函数

订阅股票更新 传入回调函数，订阅的股票有更新时，系统会调用回调函数，最多订阅100条

回调函数格式定义为on_data(datas) datas格式为 {"Code":"XXXXXX.XX","ErrorId":"0"}

接口使用

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

from tqcenter import tq

tq.initialize(__file__)

# 回调函数 功能为收到更新后请求最新的report数据

def my_callback_func(data_str):

    print("Callback received data:", data_str)

    code_json = json.loads(data_str)

    print(f"codes = {code_json.get('Code')}")

    report_ptr = tq.get_report_data(code_json.get('Code'))

    print(report_ptr)

    return None

sub_hq = tq.subscribe_hq(stock_list=['688318.SH'], callback=my_callback_func)

print(sub_hq)

# 收到更新时策略需要正在运行

#while True:

#

time.sleep(1)

数据样本

1

2

3

4

5

{

   "Error" : "订阅688318.SH更新成功.",

   "ErrorId" : "0",

   "run_id" : "1"

}

 通达信量化平台
← 初始化initialize

取消订阅更新unsubscribe_hq →

 通达信量化平台

取消订阅更新unsubscribe_hq

取消订阅股票实时更新

1

unsubscribe_hq(stock_list: List[str] = []):

输入参数

参数

stock_list

是否必选

参数类型

参数说明

Y

List[str]

证券代码

订阅股票更新 传入回调函数，订阅的股票有更新时，系统会调用回调函数，最多订阅100条

回调函数格式定义为on_data(datas) datas格式为 {"Code":"XXXXXX.XX","ErrorId":"0"}

接口使用

1

2

3

4

数据样本

1

2

3

4

5

from tqcenter import tq

tq.initialize(__file__)

un_sub_ptr = tq.unsubscribe_hq(stock_list=['688318.SH'])

print(un_sub_ptr)

{

   "Error" : "取消全部订阅更新失败.",

   "ErrorId" : "0",

   "run_id" : "1"

}

py

py

← 订阅行情subscribe_hq

获得订阅列表get_subscribe_hq_stock_list →

 通达信量化平台

获得订阅列表get_subscribe_hq_stock_list

获得当前策略订阅的股票列表

1

get_subscribe_hq_stock_list():

接口使用

1

2

3

4

5

6

from tqcenter import tq

tq.initialize(__file__)

sub_list = tq.get_subscribe_hq_stock_list()

print(sub_list)

数据样本

1

['600519.SH']

py

py

← 取消订阅更新unsubscribe_hq

刷新行情缓存refresh_cache →

 通达信量化平台

刷新行情缓存(最新snapshot和K线数据)refresh_cache

刷新行情缓存(最新snapshot和K线数据)。如果不调用，首次取snapshot和K线时系统会自动刷新一次行情

def refresh_cache(market: str = 'AG',

force: bool = False):

py

1

2

输入参数

参数

是否必选

参数类型

参数说明

force

market

Y

Y

bool

str

是否强制刷新

指定刷新的市场

force为false时距离上次刷新不足10分钟则不会刷新，为true时强制刷新。

market赋值： 'AG'表示A股，'HK'表示港股，'US'表示美股，'QH'表示国内期货，'QQ'表示股票期权，'NQ'表示新三板，'ZZ'表

示中证和国证指数。

py

from tqcenter import tq

tq.initialize(__file__)

refresh_cache = tq.refresh_cache()

print(refresh_cache)

接口使用

1

2

3

4

5

数据样本

使用后会在客户端弹出刷新数据的加载界面，加载完成后才会有返回

1

2

3

4

5

{

   "Error" : "Refresh Cache Success.",

   "ErrorId" : "0",

   "run_id" : "1"

}

← 获得订阅列表get_subscribe_hq_stock_list

缓存历史K线refresh_kline →

 通达信量化平台

刷新历史K线缓存refresh_kline

根据股票和周期刷新历史K线缓存，如果本地没有下载完整的日线等数据，则可以调用这个函数定向下载某些品种某些周期的历
史K线数据

1

refresh_kline(stock_list: List[str] = [], period: str = '')

py

输入参数

参数

stock_list

period

接口使用

是否必选

参数类型

参数说明

Y

Y

List[str]

证券代码列表，证券代码格式为6位数+市场后缀（.SH/.SZ/.BJ
等）

str

周期 1d为日线、1m为一分钟线、5m为五分钟线，只支持这三
种，其它周期的数据均由这三种数据生成

from tqcenter import tq

tq.initialize(__file__)

refresh_kline = tq.refresh_kline(stock_list=['688318.SH'],period='1d')

print(refresh_kline)

py

1

2

3

4

数据样本

注：如果在盘中交易时间段下载1m和5m分钟线，只能下载到截止上个交易日的数据

使用后会在客户端弹出刷新数据的加载界面，加载完成后才会有返回

1

2

3

4

5

{

   "Error" : "refresh kline cache success.",

   "ErrorId" : "0",

   "run_id" : "1"

}

← 刷新行情缓存refresh_cache

下载特定数据文件download_file →

 通达信量化平台

发送消息到通达信客户端send_message

发送消息给通达信客户端的TQ策略界面

1

send_message(msg_str: str) -> Dict:

输入参数

参数

是否必选

参数类型

参数说明

msg_str

Y

str

消息字符串

传入的字符串使用 | 可以让客户端将其分为两条（插入 \n 也可以分行显示）

接口使用

1

2

3

4

from tqcenter import tq

tq.initialize(__file__)

msg_str = "这是第一行. | 这是第二行. "

tq.send_message(msg_str)

py

py

← 获取交易日列表get_trading_dates

发送预警信号到客户端send_warn →

 通达信量化平台

发送预警信号send_warn

往客户端发送指定股票的预警信号

1

2

3

4

5

6

7

8

9

send_warn(stock_list:        List[str] = [],

py

time_list:         List[str] = [],

price_list:        List[str] = [],

close_list:        List[str] = [],

volum_list:        List[str] = [],

bs_flag_list:      List[str] = [],

warn_type_list:    List[str] = [],

reason_list:       List[str] = [],

count:        int  = 1) -> Dict:

输入参数

参数

stock_list

time_list

price_list

close_list

volum_list

bs_flag_list

warn_type_list

reason_list

count

是否必选

参数类型

参数说明

Y

Y

N

N

N

N

N

N

N

List[str]

证券代码列表

List[str]

时间列表

List[str]

现价列表

List[str]

收盘价列表

List[str]

成交额列表

List[str]

买卖标志：0买1卖2未知

List[str]

预警类型：0常规预警（目前仅支持）

List[str]

预警原因

int

有效数据个数

price_list、close_list、volum_list、bs_flag_list、warn_type_list 均要求为纯数字字符串List

bs_flag_list 0买1卖2未知，长度小于count的会自动补为2。

reason_list每个元素有效长度为25个汉字（50个英文）|

count限定入参中每个list中的有效数据个数，即每个list前count个数据会传给客户端

stock_list与其他list的元素数据是一一对应的，即stock_list的第一个元素对应的预警信息是其他list的第一个元素，同一只股票

的多个预警信息，则在stock_list中加入多次该股票

接口使用

1

2

3

4

5

6

7

8

9

from tqcenter import tq

tq.initialize(__file__)

warn_res = tq.send_warn(stock_list = ['688318.SH','688318.SH','600519.SH'],

             time_list = ['20251215141115','20251215142100','20251215143101'],

             price_list= ['123.45','133.45','1823.45'],

             close_list= ['122.50','132.50','1822.50'],

             volum_list= ['1000','2000','15000'],

             bs_flag_list= ['0'],

             warn_type_list= ['0'],

10

             reason_list= ['价格突破预警线','收盘价突破预警线','成交量突破预警线'],

py

11

             count=3)

 通达信量化平台

print(warn_res)

12

数据样本

1

{'Error': '发送预警信号成功.', 'ErrorId': '0', 'run_id': '1'}

← 发送消息到TQ策略界面send_message

发送文件到客户端send_file →

 通达信量化平台

发送文件到客户端send_file

往通达信客户端发送文件名，可由TQ策略数据浏览中打开

1

send_file(file: str) -> Dict:

输入参数

参数

是否必选

参数类型

参数说明

file

Y

str

文件路径

文件放于 .\PYPlugins\file\ 文件夹中时，file可仅传入文件名

文件放于其他位置时，file需要传入绝对路径

目前支持的文件类型：txt，pdf，html

接口使用

1

2

3

4

from tqcenter import tq

tq.initialize(__file__)

file = "test.txt"

tq.send_file(file)

py

py

← 发送预警信号到客户端send_warn

发送回测数据send_bt_data →

 通达信量化平台

发送回测数据send_bt_data

往客户端发送指定股票的回测数据

1

2

3

4

send_bt_data(stock_code:          str  = '',

time_list:         List[str] = [],

data_list:         List[List[str]] = [],

count:        int  = 1) -> Dict:

py

输入参数

参数

stock_code

time_list

data_list

count

是否必选

参数类型

参数说明

Y

Y

N

N

List[str]

List[str]

证券代码

时间列表

List[List[str]]

回测数据列表

int

有效数据个数

data_list为二维List，每个子元素对应time_list的一个元素时间点，且每个子元素最多有16个有效纯数字字符串，即data_list每

个子List的前16个数据为一个时间点的有效数据

count限定入参中每个list中的有效数据个数，即每个list前count个数据会传给客户端

from tqcenter import tq

tq.initialize(__file__)

bt_data = tq.send_bt_data(stock_code = '688318.SH',

                          time_list = ['20251215141115'],

                          data_list = [['11']],

                          count = 1)

print(bt_data)

接口使用

1

2

3

4

5

6

7

8

9

数据样本

1

{'Error': '发送回测结果成功.', 'ErrorId': '0', 'run_id': '1'}

py

← 发送文件到客户端send_file

打印数据到客户端print_to_tdx →

py

py

 通达信量化平台

下载特定数据文件download_file

10大股东数据文件、ETF申赎清单文件、最近舆情信息文件、股票综合信息文件

1

2

3

download_file(stock_code: str = '',

down_time:str = '',

down_type:int = 1):

输入参数

参数

stock_code

down_time

down_type

是否必选

参数类型

参数说明

Y

Y

Y

List[str]

证券代码

List[str]

指定时间

List[str]

指定下载类型

down_type=1时，下载10大股东数据文件，down_time只生效年份

down_type=2时，下载ETF申赎清单文件，down_time生效到日期

down_type=3时，下载最近舆情信息文件，其余两项无效

down_type=4时，下载股票综合信息文件，其余两项无效

下载的文件保存在 .\PYPlugins\data 文件夹

接口使用

1

2

3

4

5

6

7

8

数据样本

1

2

3

4

5

6

7

8

9

10

11

from tqcenter import tq

tq.initialize(__file__)

# 下载10大股东数据

down_ptr_10 = tq.download_file(stock_code='688318.SH', down_time='20250101',down_type=1)

print(down_ptr_10)

# 下载ETF申赎数据

dowm_ptr_etf = tq.download_file(stock_code='159109.SH', down_time='20250101',down_type=2)

print(dowm_ptr_etf)

{

   "ErrorId" : "0",

   "Msg" : "下载十大股东数据[2025]成功。",

   "run_id" : "1"

}

{

   "ErrorId" : "0",

   "Msg" : "下载ETF申述清单[20250101]成功。",

   "run_id" : "1"

}

 通达信量化平台

← 缓存历史K线refresh_kline

获取交易日列表get_trading_dates →

 通达信量化平台

获取交易日列表get_trading_dates

根据指定时间段获取交易日列表

1

2

3

4

get_trading_dates(market: str,

start_time: str,

end_time: str,

count:int = -1) -> List:

输入参数

参数

market

start_time

end_time

count

是否必选

参数类型

参数说明

Y

N

N

N

str

str

str

int

市场代码（暂固定为SH）

起始日期

结束日期

返回最近的count个交易日

需要现在客户端下载上证指数（999999）的盘后数据 目前仅支持A股

count > 0时，限制返回从结束日期往前最近的count个在限定时间段中的交易日

from tqcenter import tq

tq.initialize(__file__)

trade_dates = tq.get_trading_dates(market = 'SH', start_time = '20220101', end_time = '', count = 10);

print(trade_dates)

接口使用

1

2

3

4

5

6

数据样本

py

py

1

['20251211', '20251212', '20251215', '20251216', '20251217', '20251218', '20251219', '20251222', '20251223', '2

← 下载特定数据文件download_file

发送消息到TQ策略界面send_message →

 通达信量化平台

导出多组数据到通达信客户端 print_to_tdx

将计算数据导出到通达信客户端展示

print_to_tdx(df_list:          list[pd.DataFrame] = [],

py

sp_name:          str  = "",

xml_filename:     str  = "",

jsn_filenames:    list[str] = None,

vertical:         int  = None,

horizontal:       int  = None,

height:           list[str | float] = None,

table_names:      list[str] = None) -> None:

是否必选

参数类型

参数说明

Y

N

N

Y

N

N

N

N

list[pd.DataFrame]

str

str

list[str]

int

int

list[str | float]

list[str]

多组数据的DataFrame列表，每组table对
应1个DataFrame；每个DataFrame非空且
第一列为日期（datetime64[ns]或字符串类
型），后续列为指标/因子名称；列表长度
需等于组数

生成.sp文件的名称前缀，为空时默认生成
python.sp

生成的xml文件名（需包含.xml后缀），为
空会影响通达信面板配置关联，建议必填

每组数据对应的.jsn文件名列表，列表非空
且长度需等于组数（与df_list一致），文件
名建议包含.jsn后缀

纵向排列的table组数（≥1），与horizontal
二选一，horizontal优先级更高

横向排列的table组数（≥1），优先级高于
vertical，未指定时默认使用vertical或1组

自定义每组gridctrl高度列表，长度需等于
组数；元素为数值/字符串（高度占比），
未指定时自动计算（1/组数，最后一组高度
为0）

每组展示面板的标题列表，长度需等于组
数；元素为空时自动使用对应jsn_filenames
的前缀作为标题

df_list、jsn_filenames长度必须与vertical/horizontal指定的组数完全一致，否则会抛出ValueError异常

height参数值为高度占比（如0.3/"0.3"），表示该面板占整体展示区域的比例，仅支持0-1之间的数值

未指定vertical/horizontal时，默认按1组纵向排列展示，自动计算面板高度

1

2

3

4

5

6

7

8

9

输入参数

参数

df_list

sp_name

xml_filename

jsn_filenames

vertical

horizontal

height

table_names

 通达信量化平台

← 发送回测数据send_bt_data

获取K线数据get_market_data →

 通达信量化平台

获取K线行情get_market_data

根据股票，获取历史行情

1

2

3

4

5

6

7

8

get_market_data(field_list: List[str] = [],

stock_list: List[str] = [],

period: str = '',

start_time: str = '',

end_time: str = '',

count: int = -1,

dividend_type: Optional[str] = None,

fill_data: bool = True) -> Dict:

py

输入参数

参数

field_list

stock_list

period

start_time

end_time

count

dividend_type

fill_data

返回参数

是否必选

参数类型

参数说明

N

Y

Y

N

N

N

N

N

List[str]

字段筛选，传空则返回全部

List[str]

证券代码列表

str

str

str

int

str

周期

起始时间

结束时间

返回数据个数（每只股票）

复权类型  ：none不复权、front前复权、back后复权

bool

是否向后填充空缺数据

返回dict { field1 : value1, field2 : value2, ... }

field1, field2, ... ：数据字段

value1, value2, ... ：pd.DataFrame 数据集，index为stock_list，columns为time_list

各字段对应的DataFrame维度相同、索引相同

只有dividend_type传入为none时，会返回有效的前复权因子ForwardFactor

一次最多返回24000条数据，要获取完整分钟线需要多次分批获取

参数

Date

Time

Open

High

Low

默认返回

参数类型

参数说明

Y

Y

Y

Y

Y

str

str

str

str

str

日期

时间

开盘价

最高价

最低价

py

参数

 通达信量化平台

默认返回

参数类型

参数说明

Close

Volume

Amount

ForwardFactor

接口使用

Y

Y

Y

Y

str

str

str

str

收盘价

成交量

成交额

前复权因子，当dividend_type=none时候返回有效值

获取688318.SH从2025-12-20到今为止最新一条日K线的不复权数据

1

2

3

4

5

6

7

8

9

10

11

12

13

from tqcenter import tq

tq.initialize(__file__)

df = tq.get_market_data(

        field_list=[],

        stock_list=['688318.SH'],

        start_time='20251220',

        end_time='',

        count=1,

        dividend_type='none',

        period='1d',

        fill_data=True

    )

print(df)

数据样本

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

{'Amount':             688318.SH

2025-12-24   29394.81,

'Low':             688318.SH

2025-12-24      128.0,

'Date':              688318.SH

2025-12-24  20251224.0,

'Volume':             688318.SH

2025-12-24  2257325.0,

'Close':             688318.SH

2025-12-24     131.58,

'Open':             688318.SH

2025-12-24     128.01,

'Time':             688318.SH

2025-12-24        0.0,

'High':             688318.SH

2025-12-24     131.87,

'ForwardFactor':             688318.SH

2025-12-24        1.0}

← 打印数据到客户端print_to_tdx

获取快照数据get_market_snapshot →

 通达信量化平台

获取快照数据get_market_snapshot

根据股票，获取最新行情数据

1

2

def get_market_snapshot(stock_code: str,

                    field_list: List = []) -> Dict:

py

输入参数

参数

stock_code

field_list

返回参数

参数

ItemNum

LastClose

Open

Max

Min

Now

Volume

NowVol

Amount

Inside

Outside

TickDiff

InOutFlag

Jjjz

Buyp

Buyv

Sellp

Sellv

UpHome

是否必选

参数类型

参数说明

Y

N

str

证券代码

List[str]

字段筛选，传空则返回全部

默认返回

参数类型

参数说明

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

str

str

str

str

str

str

str

str

str

str

str

str

str

str

快照笔数

前收盘价

开盘价

最高价

最低价

现价

总手

现手

总成交金额

内盘

外盘

笔涨跌

内外盘标志 0:Buy 1:Sell 2:Unknown

基金净值

List[str]

五个买价

List[str]

对应的五个买盘量

List[str]

五个卖价

List[str]

对应的五个卖盘量

str

上涨家数 对于指数有效

参数

 通达信量化平台

DownHome

Before5MinNow

Average

XsFlag

Zangsu

ZAFPre3

接口使用

默认返回

参数类型

参数说明

Y

Y

Y

Y

Y

Y

str

str

str

str

str

str

下跌家数 对于指数有效

5分钟前价格

均价

小数位数

涨速

3日涨幅

获取688318.SH从2025-12-20到今为止最新一条日K线的不复权数据

1

2

3

4

5

6

数据样本

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

from tqcenter import tq

tq.initialize(__file__)

market_snapshot = tq.get_market_snapshot(stock_code = '688260.SH', field_list=[])

print(market_snapshot)

py

{'ItemNum': '3342',

'LastClose': '34.21',

'Open': '33.78',

'Max': '36.49',

'Min': '32.50',

'Now': '35.06',

'Volume': '122881',

'NowVol': '1449',

'Amount': '43068.48',

'Inside': '60373',

'Outside': '62509',

'TickDiff': '0.00',

'InOutFlag': '2',

'Jjjz': '0.00',

'Buyp': ['35.05', '35.04', '35.02', '35.01', '35.00'],

'Buyv': ['154', '9', '49', '136', '154'],

'Sellp': ['35.06', '35.07', '35.08', '35.09', '35.10'],

'Sellv': ['4', '31', '139', '4', '4'],

'UpHome': '0',

'DownHome': '0',

'Before5MinNow': '35.15',

'Average': '35.05',

'XsFlag': '2',

'Zangsu': '-0.25',

'ZAFPre3': '-1.83',

'ErrorId': '0'}

 通达信量化平台

← 获取K线数据get_market_data

获取证券基本信息get_stock_info →

 通达信量化平台

获取证券基本信息get_stock_info

根据股票，获取股票基础的财务数据

1

2

3

get_stock_info(cls,

stock_code:str,

field_list: List = []) -> Dict:

py

输入参数

参数

stock_code

field_list

返回参数

参数

Name

Unit

VolBase

MinPrice

XsFlag

Fz[8]

DelayMin

QHVolBaseRate

HKVolBaseRate

BelongHS300

BelongHasKQZ

BelongRZRQ

BelongHSGT

IsHKGP

IsQH

IsQQ

IsSTGP

IsQuitGP

TodayDRFlag

是否必选

参数类型

参数说明

Y

Y

str

证券代码

List[str]

字段筛选，不能为空

默认返回

参数类型

参数说明

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

str

str

str

str

str

证券名称

交易单位

量比的基量

最小价格变动

价格小数位数

List[str]

开收市时间（4段）

str

str

str

str

str

str

str

str

str

str

str

str

str

延时分钟数

期货期权的每手乘数

港股/日股/新加坡股 每手股数

是否属于沪深300

是否含可转债

是否是融资融券标的

是否属于沪深股通

是否是港股

是否是期货

是否是期权

是否是ST股票

是否是退市整理板股票

当天是否有除权除息(沪深京)

参数

 通达信量化平台

HSStockKind

ActiveCapital

J_zgb

J_bg

J_hg

J_zzc

J_ldzc

J_gdzc

J_wxzc

J_ldfz

J_cqfz

J_zbgjj

J_jzc

J_yysy

J_yycb

J_yszk

J_yyly

J_tzsy

J_jyxjl

J_zxjl

J_ch

J_lyze

J_shly

J_jly

J_wfply

J_jyl

J_mgwfp

J_mgsy

J_mgsy2

J_mggjj

J_mgjzc

J_mgjzc2

默认返回

参数类型

参数说明

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

沪深京品种类型 0:指数,1:A股主板,2:北证A股,3:创业板,4:科创
板,5:B股,6:债券,7:基金,8:权证,9:其它,10:非沪深京品种

流通股本(万股)

总股本(万股)

B股(万股)

H股(万股)

总资产(万元)

流动资产(万元)

固定资产(万元)

无形资产(万元)

流动负债(万元)

少数股东权益(万元)

资本公积金(万元)

股东权益/净资产(万元)

营业收入(万元)

营业成本(万元)

应收账款(万元)

营业利润(万元)

投资收益(万元)

经营现金净流量(万元)

总现金净流量(万元)

存货(万元)

利润总额(万元)

税后利润(万元)

净利润(万元)

未分配利益(万元)

净资产收益率

每股未分配

每股收益（折算为全年）

季报每股收益 (财报中提供的每股收益)

每股公积金

每股净资产

季报每股净资产 (财报中提供的每股收益)

参数

 通达信量化平台

默认返回

参数类型

参数说明

J_gdqyb

J_gdrs

J_HalfYearFlag

J_start

tdx_dycode

tdx_dyname

rs_hycode_sim

rs_hyname

blockzscode

underly_setcode

underly_code

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

str

str

str

str

str

str

str

str

str

str

str

股东权益比

股东人数

报告期月份(3,6,9,12)

上市日期

通达信地域代码

通达信地域

通达信行业代码

通达信行业

所属的行业板块指数代码

标的市场代码

标的代码

接口使用

1

2

3

4

数据样本

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

from tqcenter import tq

tq.initialize(__file__)

fdc = tq.get_stock_info(stock_code='688318.SH', field_list=[])

print(fdc)

py

{'Name': '财富趋势',

'Unit': '100',

'VolBase': '102.22',

'MinPrice': '0.01',

'XsFlag': '2',

'Fz': ['570', '690', '780', '900', '900', '900', '900', '900'],

'DelayMin': '0',

'QHVolBaseRate': '0',

'HKVolBaseRate': '0',

'BelongHS300': '0',

'BelongHasKQZ': '0',

'BelongRZRQ': '1',

'BelongHSGT': '1',

'IsHKGP': '0',

'IsQH': '0',

'IsQQ': '0',

'IsSTGP': '0',

'IsQuitGP': '0',

'TodayDRFlag': '0',

'HSStockKind': '4',

'ActiveCapital': '25611.94',

'J_zgb': '25611.94',

'J_bg': '0.00',

'J_hg': '0.00',

'J_zzc': '389036.97',

'J_ldzc': '235598.84',

27

'J_gdzc': '972.62',

 通达信量化平台

28

'J_wxzc': '1184.64',

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

53

54

55

56

57

58

59

60

61

62

63

'J_ldfz': '17412.97',

'J_cqfz': '73.15',

'J_zbgjj': '157998.02',

'J_jzc': '370454.03',

'J_yysy': '19827.85',

'J_yycb': '4258.70',

'J_yszk': '2726.99',

'J_yyly': '20836.07',

'J_tzsy': '5091.96',

'J_jyxjl': '5432.08',

'J_zxjl': '9779.30',

'J_ch': '61.84',

'J_lyze': '20829.85',

'J_shly': '18421.45',

'J_jly': '18421.34',

'J_wfply': '175521.63',

'J_jyl': '4.97',

'J_mgwfp': '6.85',

'J_mgsy': '0.96',

'J_mgsy2': '0.00',

'J_mggjj': '6.17',

'J_mgjzc': '14.46',

'J_mgjzc2': '14.46',

'J_gdqyb': '0.95',

'J_gdrs': '24154.00',

'J_HalfYearFlag': '9',

'J_start': '20200427',

'tdx_dycode': '18',

'tdx_dyname': '深圳板块',

'rs_hycode_sim': 'X4202',

'rs_hyname': '软件服务',

'blockzscode': '881355',

'underly_setcode': '0',

'underly_code': '',

'ErrorId': '0'}

← 获取快照数据get_market_snapshot

获取股票更多信息get_more_info →

 通达信量化平台

获取股票更多信息get_more_info

获取指定股票更细节的信息

1

2

def get_more_info(stock_code:str = '',

field_list: List = []):

py

输入参数

参数

stock_code

field_list

返回参数

参数

MainBusiness

SafeValue

ShineValue

ShapeValue

TPFlag

ZTPrice

DTPrice

HqDate

fHSL

fLianB

Wtb

Zsz

Ltsz

vzangsu

Fzhsl

FzAmo

VOpenZAF

ZAF

是否必选

参数类型

参数说明

Y

N

str

股票代码

List[str]

字段筛选，传空则返回全部

默认返回

参数类型

参数说明

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

主营构成

安全分

亮点数

短期形态+中期形态+长期形态 编号

停牌标识

涨停价

跌停价

行情日期

换手率

量比

委比

总市值(亿)

流通市值(亿)

量涨速

分钟换手率

2分钟金额(万元)

抢筹涨幅

涨幅

参数

 通达信量化平台

ZAFYesterday

ZAFPre2D

ZAFPre5

ZAFPre10

ZAFPre20

ZAFPre30

ZAFPre60

ZAFYear

ZAFPreMyMonth

ZAFPreOneYear

Zjl

Zjl_HB

TotalBVol

TotalSVol

BCancel

SCancel

L2TicNum

L2OrderNum

FCAmo

FCb

OpenAmo

OpenFDE

OpenAmoPre1

OpenVolPre1

CJJEPre1

CJJEPre3

FDEPre1

FDEPre2

ZTGPNum

LastStartZT

默认返回

参数类型

参数说明

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

昨日涨幅

前天涨幅

5日涨幅

10日涨幅

20日涨幅

30日涨幅

60日涨幅

年初至今涨幅

涨幅(本月来)

涨幅(一年来)

主买净额(万元)

主力净流入(万元)

总买量

总卖量

总撤买量

总撤卖量

L2逐笔成交数

L2逐笔委托数

封单额(万元)

封成比

开盘金额(万元)(A股和板块指数有效)

开盘封单额(万元)

昨开盘金额(万元)

昨开盘量

昨成交额(万元)

3日成交额(万元)

昨封单额(万元)

前封单额(万元)

板块指数的涨停家数

几天

参数

 通达信量化平台

默认返回

参数类型

参数说明

LastZTHzNum

EverZTCount

ConZAFDateNum

YearZTDay

MA5Value

HisHigh

HisLow

IPO_Price

More_YJL

BetaValue

DynaPE

MorePE

StaticPE_TTM

DYRatio

PB_MRQ

IsT0Fund

IsZCZGP

IsKzz

Kzz_HSCode

FreeLtgb

Yield

KfEarnMoney

RDInputFee

CashZJ

PreReceiveZJ

OtherQYJzc

StaffNum

RecentGGJYDate

RecentHGDate

RecentIncentDate

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

str

几板

连板天

连涨天数

年涨停天数

5日均价

52周最高

52周最低

发行价

ETF,LOF溢价率

贝塔系数

动态市盈率

市盈率(港股:动,其他扩展:静)

市盈率(TTM)

股息率

市净率(MRQ)

是否是T+0基金

是否是注册制A股

是否是可转债

可转债对应的正股代码

自由流通股本(万)

应计利息(债券),占款天数(回购)

扣非净利润(万元)

研发费用(万元)

货币资金(万元)

合同负债(万元)

其它权益工具(万元)

员工人数

最近北上大额交易日

最近回购预案日

最近股权激励预案日

参数

 通达信量化平台

NoticeDate_Recent

RecentReleaseDate

RecentDZDate

ReportDate

ZTDate_Recent

DTDate_Recent

TopDate_Recent

StopJYDate_Recent

默认返回

参数类型

参数说明

Y

Y

Y

Y

Y

Y

Y

Y

str

str

str

str

str

str

str

str

最近业绩预告日

最近解禁日

最近定增日

最近财报公告日期

近2年最近涨停板日期

近2年最近跌停板日期

近2年最近龙虎榜日期

最近停牌日期

from tqcenter import tq

tq.initialize(__file__)

more_info = tq.get_more_info(stock_code = '688318.SH', field_list=[])

print(more_info)

py

接口使用

1

2

3

4

数据样本

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

{'MainBusiness': '软件服务收入',

'SafeValue': '98',

'ShineValue': '3',

'ShapeValue': '101308',

'TPFlag': '0',

'ZTPrice': '151.62',

'DTPrice': '101.08',

'HqDate': '20260227',

'fHSL': '0.86',

'fLianB': '0.89',

'Wtb': '-0.66',

'Zsz': '326.91',

'Ltsz': '326.91',

'vzangsu': '2.17',

'Fzhsl': '0.12',

'FzAmo': '514.92',

'VOpenZAF': '0.00',

'ZAF': '1.02',

'ZAFYesterday': '-1.21',

'ZAFPre2D': '1.99',

'ZAFPre5': '-1.56',

'ZAFPre10': '-3.44',

'ZAFPre20': '-10.76',

'ZAFPre30': '-10.13',

'ZAFPre60': '-1.59',

'ZAFYear': '-3.54',

'ZAFPreMyMonth': '-5.23',

'ZAFPreOneYear': '10.27',

'Zjl': '0.00',

'Zjl_HB': '0.00',

'TotalBVol': '1295.00',

'TotalSVol': '3555.00',

'BCancel': '42606.00',

34

'SCancel': '40266.00',

 通达信量化平台

35

'L2TicNum': '6880',

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

53

54

55

56

57

58

59

60

61

62

63

64

65

66

67

68

69

70

71

72

73

74

75

76

77

78

79

80

81

82

83

84

85

86

'L2OrderNum': '29448',

'FCAmo': '0.00',

'FCb': '0.00',

'OpenAmo': '1069400.00',

'OpenFDE': '0.00',

'OpenAmoPre1': '77.93',

'OpenVolPre1': '61.00',

'CJJEPre1': '26056.68',

'CJJEPre3': '89751.03',

'FDEPre1': '0.00',

'FDEPre2': '0.00',

'ZTGPNum': '0',

'LastStartZT': '0',

'LastZTHzNum': '0',

'EverZTCount': '0',

'ConZAFDateNum': '1',

'YearZTDay': '0',

'MA5Value': '126.56',

'HisHigh': '180.86',

'HisLow': '83.41',

'IPO_Price': '107.41',

'More_YJL': '0.00',

'BetaValue': '2.31',

'DynaPE': '133.10',

'MorePE': '107.56',

'StaticPE_TTM': '94.99',

'DYRatio': '0.28',

'PB_MRQ': '8.82',

'IsT0Fund': '0',

'IsZCZGP': '1',

'IsKzz': '0',

'Kzz_HSCode': '0',

'FreeLtgb': '7935.14',

'Yield': '106.94',

'KfEarnMoney': '9778.22',

'RDInputFee': '5894.58',

'CashZJ': '60954.52',

'PreReceiveZJ': '11281.48',

'OtherQYJzc': '0.00',

'StaffNum': '446',

'RecentGGJYDate': '0',

'RecentHGDate': '0',

'RecentIncentDate': '0',

'NoticeDate_Recent': '0',

'RecentReleaseDate': '20230427',

'RecentDZDate': '0',

'ReportDate': '20251031',

'ZTDate_Recent': '20241008',

'DTDate_Recent': '0',

'TopDate_Recent': '20250625',

'StopJYDate_Recent': '0'}

← 获取证券基本信息get_stock_info

获取分红配送数据get_divid_factors →

 通达信量化平台

获取分红配送数据get_divid_factors

根据股票，获取指定时间段内的分红配送数据

1

2

3

get_divid_factors(stock_code: str,

start_time: str,

end_time: str) -> pd.DataFrame:

输入参数

参数

stock_code

start_time

end_time

返回参数

参数

Type

Bonus

AlloPrice

ShareBonus

Allotment

接口使用

是否必选

参数类型

参数说明

Y

N

N

str

str

str

证券代码

起始时间

结束时间

默认返回

参数类型

参数说明

Y

Y

Y

Y

Y

str

str

str

str

str

类型 1:除权除息 11:扩缩股 15:重新调整

红利

配股价

送股/扩缩股比例

配股

获取688318.SH全部分红配送数据

1

2

3

4

5

6

7

from tqcenter import tq

tq.initialize(__file__)

divid_factors = tq.get_divid_factors(

        stock_code='688318.SH',

        start_time='',

        end_time='')

print(divid_factors)

数据样本

1

2

3

4

5

           Type  Bonus  AllotPrice  ShareBonus  Allotment

Date

2020-09-29    1    6.0         0.0         0.0        0.0

2021-05-27    1   10.0         0.0         0.0        0.0

2022-06-20    1   14.0         0.0         4.0        0.0

2023-06-13    1    5.0         0.0         4.0        0.0

py

py

6

2024-06-14    1    8.0         0.0         4.0        0.0

 通达信量化平台

7

← 获取股票更多信息get_more_info

获取新股申购信息get_ipo_info →

 通达信量化平台

获取新股申购信息get_ipo_info

获取今天及未来的新股或新发债申购信息

1

2

get_ipo_info(ipo_type:int = 0,

             ipo_date:int = 0):

输入参数

参数

是否必选

参数类型

参数说明

ipo_type

ipo_date

Y

Y

str

int

自定义板块简称

自定义板块名称

ipo_type=0 表示获取新股申购信息

ipo_type=1 表示获取新发债信息

ipo_type=2 表示获取新股和新发债信息

ipo_date=0 表示只获取今天信息

ipo_date=1 表示获取今天及以后信息

接口使用

1

2

3

4

数据样本

1

2

from tqcenter import tq

tq.initialize(__file__)

ipo_info = tq.get_ipo_info(ipo_type=2, ipo_date=1)

print(ipo_info)

[{'MaxSG': '0.00', 'PE_Issue': '0.00', 'SGCode': '371036', 'SGDate': '20251226', 'SGPrice': '100.00', 'code': '

{'MaxSG': '0.00', 'PE_Issue': '0.00', 'SGCode': '718676', 'SGDate': '20251225', 'SGPrice': '100.00', 'code': '6

← 获取分红配送数据get_divid_factors

获取每天的股本数据get_gb_info →

py

py

 通达信量化平台

获取每天的股本数据get_gb_info

获取指定股票的股本数据

1

2

3

def get_gb_info(stock_code:str = '',

                date_list: List[str] = [],

                count: int = 1):

输入参数

参数

stock_code

date_list

count

是否必选

参数类型

参数说明

Y

Y

Y

str

股票代码

List[str]

日期数组

int

日期有效个数

date_list传入的日期须从小到大排序

date_list有效数据个数须不小于count，且不能小于1

输出参数

名称

类型

数值

说明

Date

double

Zgb

double

日期

总股本

Ltgb

double

流通股本

from tqcenter import tq

tq.initialize(__file__)

gb_info = tq.get_gb_info(stock_code = '688318.SH', date_list=['20250101','20250601'], count=2)

print(gb_info)

接口使用

1

2

3

4

数据样本

1

2

[{'Date': 20250101, 'Zgb': 182942480.0, 'Ltgb': 182942480.0},

{'Date': 20250601,  'Zgb': 182942480.0, 'Ltgb': 182942480.0}]

py

py

← 获取新股申购信息get_ipo_info

获取专业财务数据get_financial_data →

 通达信量化平台

获取专业财务数据get_financial_data

根据股票，获取指定时间段内的专业财务数据，与基础财务数据不同，需要先在客户端中下载专业财务数据

1

2

3

4

5

get_financial_data(stock_list: List[str] = [],

py

field_list: List[str] = [],

start_time: str = '',

end_time: str = '',

report_type: str = 'report_time') -> Dict:

输入参数

参数

stock_list

field_list

start_time

end_time

report_type

输出参数

名称

announce_time

tag_time

FN1

FN2

FN3

FN4

FN5

FN6

FN7

FN8

FN9

FN10

FN11

是否必选

参数类型

参数说明

Y

Y

Y

N

N

List[str]

证券代码列表例如  ["600519.SH"]

List[str]

str

str

bool

字段筛选，不能为空，字段名须与系统定义一致（如

FN193 ）

起始时间，格式  YYYYMMDD ，如  '20250101'

结束时间，格式  YYYYMMDD ，为空表示无结束限制

按截止日期还是公告日期筛选，可选
值： 'announce_time' （按公告日期筛选）或

'tag_time' （按报告期筛选）

类型

数值

说明

int

int

double

double

double

double

double

double

double

double

double

double

double

公告日期

报告期

基本每股收益

扣除非经常性损益每股收益

每股未分配利润

每股净资产

每股资本公积金

净资产收益率

每股经营现金流量

货币资金

交易性金融资产

应收票据

应收账款

名称

 通达信量化平台

类型

数值

说明

FN12

FN13

FN14

FN15

FN16

FN17

FN18

FN19

FN20

FN21

FN22

FN23

FN24

FN25

FN26

FN27

FN28

FN29

FN30

FN31

FN32

FN33

FN34

FN35

FN36

FN37

FN38

FN39

FN40

FN41

FN42

FN43

FN44

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

预付款项

其他应收款

应收关联公司款

应收利息

应收股利

存货

其中：消耗性生物资产

一年内到期的非流动资产

其他流动资产

流动资产合计

可供出售金融资产

持有至到期投资

长期应收款

长期股权投资

投资性房地产

固定资产

在建工程

工程物资

固定资产清理

生产性生物资产

油气资产

无形资产

开发支出

商誉

长期待摊费用

递延所得税资产

其他非流动资产

非流动资产合计

资产总计

短期借款

交易性金融负债

应付票据

应付账款

名称

 通达信量化平台

类型

数值

说明

FN45

FN46

FN47

FN48

FN49

FN50

FN51

FN52

FN53

FN54

FN55

FN56

FN57

FN58

FN59

FN60

FN61

FN62

FN63

FN64

FN65

FN66

FN67

FN68

FN69

FN70

FN71

FN72

FN73

FN98

FN99

FN100

FN101

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

预收款项

应付职工薪酬

应交税费

应付利息

应付股利

其他应付款

应付关联公司款

一年内到期的非流动负债

其他流动负债

流动负债合计

长期借款

应付债券

长期应付款

专项应付款

预计负债 （非流动负债）

递延所得税负债

其他非流动负债

非流动负债合计

负债合计

实收资本（或股本）

资本公积

盈余公积

减：库存股

未分配利润

少数股东权益

外币报表折算价差

非正常经营项目收益调整

所有者权益（或股东权益）合计

负债和所有者（或股东权益）合计

销售商品、提供劳务收到的现金

收到的税费返还

收到其他与经营活动有关的现金

经营活动现金流入小计

名称

 通达信量化平台

类型

数值

说明

FN102

FN103

FN104

FN105

FN106

FN107

FN108

FN109

FN110

FN111

FN112

FN113

FN114

FN115

FN116

FN117

FN118

FN119

FN120

FN121

FN122

FN123

FN124

FN125

FN126

FN127

FN128

FN129

FN130

FN131

FN132

FN133

FN134

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

购买商品、接受劳务支付的现金

支付给职工以及为职工支付的现金

支付的各项税费

支付其他与经营活动有关的现金

经营活动现金流出小计

经营活动产生的现金流量净额

收回投资收到的现金

取得投资收益收到的现金

处置固定资产、无形资产和其他长期资产收回的现金净额

处置子公司及其他营业单位收到的现金净额

收到其他与投资活动有关的现金

投资活动现金流入小计

购建固定资产、无形资产和其他长期资产支付的现金

投资支付的现金

取得子公司及其他营业单位支付的现金净额

支付其他与投资活动有关的现金

投资活动现金流出小计

投资活动产生的现金流量净额

吸收投资收到的现金

取得借款收到的现金

收到其他与筹资活动有关的现金

筹资活动现金流入小计

偿还债务支付的现金

分配股利、利润或偿付利息支付的现金

支付其他与筹资活动有关的现金

筹资活动现金流出小计

筹资活动产生的现金流量净额

四、汇率变动对现金的影响

四(2)、其他原因对现金的影响

五、现金及现金等价物净增加额

期初现金及现金等价物余额

期末现金及现金等价物余额

净利润

名称

 通达信量化平台

类型

数值

说明

FN135

FN136

FN137

FN138

FN139

FN140

FN141

FN142

FN143

FN144

FN145

FN146

FN147

FN148

FN149

FN150

FN151

FN152

FN153

FN154

FN155

FN156

FN157

FN158

FN159

FN160

FN161

FN162

FN163

FN164

FN166

FN167

FN168

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

加：资产减值准备

固定资产折旧、油气资产折耗、生产性生物资产折旧

无形资产摊销

长期待摊费用摊销

处置固定资产、无形资产和其他长期资产的损失

固定资产报废损失

公允价值变动损失

财务费用

投资损失

递延所得税资产减少

递延所得税负债增加

存货的减少

经营性应收项目的减少

经营性应付项目的增加

其他

经营活动产生的现金流量净额2

债务转为资本

一年内到期的可转换公司债券

融资租入固定资产

现金的期末余额

减：现金的期初余额

加：现金等价物的期末余额

减：现金等价物的期初余额

现金及现金等价物净增加额

流动比率(非金融类指标)

速动比率(非金融类指标)

现金比率(%)(非金融类指标)

利息保障倍数(非金融类指标)

非流动负债比率(%)(非金融类指标)

流动负债比率(%)(非金融类指标)

有形资产净值债务率(%)

权益乘数(%)

股东的权益/负债合计(%)

名称

 通达信量化平台

类型

数值

说明

FN169

FN170

FN171

FN172

FN173

FN174

FN175

FN176

FN177

FN178

FN179

FN180

FN181

FN182

FN183

FN184

FN185

FN186

FN187

FN188

FN189

FN190

FN191

FN192

FN193

FN194

FN195

FN196

FN197

FN198

FN199

FN200

FN201

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

有形资产/负债合计(%)

经营活动产生的现金流量净额/负债合计(%)(非金融类指标)

EBITDA/负债合计(%)(非金融类指标)

应收帐款周转率(非金融类指标)

存货周转率(非金融类指标)

运营资金周转率(非金融类指标)

总资产周转率(非金融类指标)

固定资产周转率(非金融类指标)

应收帐款周转天数(非金融类指标)

存货周转天数(非金融类指标)

流动资产周转率(非金融类指标)

流动资产周转天数(非金融类指标)

总资产周转天数(非金融类指标)

股东权益周转率(非金融类指标)

营业收入增长率(%)

净利润增长率(%)

净资产增长率(%)

固定资产增长率(%)

总资产增长率(%)

投资收益增长率(%)

营业利润增长率(%)

扣非每股收益同比(%)

扣非净利润同比(%)

暂无

成本费用利润率(%)

营业利润率(非金融类指标)

营业税金率(非金融类指标)

营业成本率(非金融类指标)

净资产收益率

投资收益率

销售净利率(%)

总资产净利率

净利润率(非金融类指标)

名称

 通达信量化平台

类型

数值

说明

FN202

FN203

FN204

FN205

FN206

FN207

FN208

FN209

FN210

FN211

FN212

FN213

FN214

FN215

FN216

FN217

FN218

FN219

FN220

FN221

FN222

FN223

FN224

FN225

FN226

FN227

FN228

FN229

FN230

FN231

FN232

FN233

FN234

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

销售毛利率(%)(非金融类指标)

三费比重(非金融类指标)

管理费用率(非金融类指标)

财务费用率(非金融类指标)

扣除非经常性损益后的净利润

息税前利润(EBIT)

息税折旧摊销前利润(EBITDA)

EBITDA/营业总收入(%)(非金融类指标)

资产负债率(%)

流动资产比率(非金融类指标)

货币资金比率(非金融类指标)

存货比率(非金融类指标)

固定资产比率

负债结构比(非金融类指标)

归属于母公司股东权益/全部投入资本(%)

股东的权益/带息债务(%)

有形资产/净债务(%)

每股经营性现金流(元)

营业收入现金含量(%)(非金融类指标)

经营活动产生的现金流量净额/经营活动净收益(%)

销售商品提供劳务收到的现金/营业收入(%)

经营活动产生的现金流量净额/营业收入

资本支出/折旧和摊销

每股现金流量净额(元)

经营净现金比率（短期债务）(非金融类指标)

经营净现金比率（全部债务）

经营活动现金净流量与净利润比率

全部资产现金回收率

营业收入

营业利润

归属于母公司所有者的净利润

扣除非经常性损益后的净利润

经营活动产生的现金流量净额

名称

 通达信量化平台

类型

数值

说明

FN235

FN236

FN237

FN238

FN239

FN240

FN241

FN242

FN243

FN244

FN245

FN246

FN247

FN248

FN249

FN250

FN251

FN252

FN253

FN254

FN255

FN256

FN257

FN258

FN259

FN260

FN261

FN262

FN263

FN264

FN265

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

投资活动产生的现金流量净额

筹资活动产生的现金流量净额

现金及现金等价物净增加额

总股本

已上市流通A股

已上市流通B股

已上市流通H股

股东人数(户)

第一大股东的持股数量

十大流通股东持股数量合计(股)

十大股东持股数量合计(股)

机构总量（家）

机构持股总量(股)

QFII机构数

QFII持股量

券商机构数

券商持股量

保险机构数

保险持股量

基金机构数

基金持股量

社保机构数

社保持股量

私募机构数

私募持股量

财务公司机构数

财务公司持股量

年金机构数

年金持股量

十大流通股东持有的流通A股合计(股)[ 注：2019半年报之前，季度报
告中，若股东持股除了流通A股、还有流通B股或流通H股，指标264
取的是包含流通B股或流通H股的流通股数]

double

第一大流通股东持股量(股)

名称

 通达信量化平台

类型

数值

说明

FN266

FN267

FN268

FN269

FN270

FN271

FN272

FN273

FN274

FN275

FN276

FN277

FN278

FN279

FN280

FN281

FN282

FN283

FN284

FN285

FN286

FN287

FN288

FN289

FN290

FN291

FN292

FN293

FN294

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

自由流通股(股)[注：1.自由流通股=已流通A股-持股5%以上股东的流
通A股（一致行动人算一起）；2.指标按报告期展示，新股在上市日
的下个报告期才有数据]

受限流通A股(股)

一般风险准备(金融类)

其他综合收益(利润表)

综合收益总额(利润表)

归属于母公司股东权益(资产负债表)

银行机构数(家)(机构持股)

银行持股量(股)(机构持股)

一般法人机构数(家)(机构持股)

一般法人持股量(股)(机构持股)

近一年净利润(元)

信托机构数(家)(机构持股)

信托持股量(股)(机构持股)

特殊法人机构数(家)(机构持股)

特殊法人持股量(股)(机构持股)

加权净资产收益率(每股指标)

扣非每股收益(单季度财务指标)

最近一年营业收入(万元)

国家队持股数量（万股)[注：本指标统计包含汇金公司、证金公司、
外汇管理局旗下投资平台、国家队基金、国开、养老金以及中科汇通
等国家队机构持股数量]

业绩预告-本期归母净利润同比增幅下限%[注：指标285至294展示未
来一个报告期的数据。例，3月31日至6月29日这段时间内展示的是中
报的数据；如果最新的财务报告后面有多个报告期的业绩预告/快
报，只能展示最新的财务报告后面的一个报告期的业绩预告/快报]

业绩预告-本期归母净利润同比增幅上限%

业绩快报-归母净利润

业绩快报-扣非净利润

业绩快报-总资产

业绩快报-净资产

业绩快报-每股收益

业绩快报-摊薄净资产收益率

业绩快报-加权净资产收益率

业绩快报-每股净资产

名称

 通达信量化平台

类型

数值

说明

FN295

FN296

FN297

FN298

FN299

FN300

FN301

FN302

FN303

FN304

FN305

FN306

FN307

FN308

FN309

FN310

FN311

FN312

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

应付票据及应付账款(资产负债表)

应收票据及应收账款(资产负债表)

递延收益(资产负债表-非流动负债)

其他综合收益(资产负债表)

其他权益工具(资产负债表)

其他收益(利润表)

资产处置收益(利润表)

持续经营净利润(利润表)

终止经营净利润(利润表)

研发费用(利润表)

其中:利息费用(利润表-财务费用)

其中:利息收入(利润表-财务费用)

近一年经营活动现金流净额

近一年归母净利润(万元)

近一年扣非净利润(万元)

近一年现金净流量(万元)

基本每股收益（单季度）

营业总收入(单季度)(万元)

FN313

double

业绩预告公告日期 [注：本指标展示未来一个报告期的数据。例,3月
31日至6月29日这段时间内展示的是中报的数据；如果最新的财务报
告后面有多个报告期的业绩预告/快报，只能展示最新的财务报告后
面的一个报告期的业绩预告/快报的数据；公告日期格式为
YYMMDD，例：190101代表2019年1月1日]

FN314

double

财报公告日期 [注：日期格式为YYMMDD,例：190101代表2019年1月
1日]

FN315

double

业绩快报公告日期 [注：本指标展示未来一个报告期的数据。例,3月
31日至6月29日这段时间内展示的是中报的数据；如果最新的财务报
告后面有多个报告期的业绩预告/快报，只能展示最新的财务报告后
面的一个报告期的业绩预告/快报的数据；公告日期格式为
YYMMDD，例：190101代表2019年1月1日]

FN316

FN317

FN318

FN319

FN320

FN321

double

近一年投资活动现金流净额(万元)

double

double

double

double

double

业绩预告-本期归母净利润下限(万元)[注：指标317至318展示未来一
个报告期的数据。例，3月31日至6月29日这段时间内展示的是中报的
数据；如果最新的财务报告后面有多个报告期的业绩预告/快报，只
能展示最新的财务报告后面的一个报告期的业绩预告/快报]

业绩预告-本期归母净利润上限(万元)

营业总收入TTM(万元)

员工总数(人)

每股企业自由现金流

名称

 通达信量化平台

类型

数值

说明

FN322

FN323

FN324

FN325

FN326

FN327

FN328

FN329

FN330

FN331

FN332

FN333

FN334

FN335

FN336

FN337

FN338

FN339

FN340

FN341

FN342

FN343

FN344

FN345

FN346

FN347

FN348

FN349

FN350

FN351

FN352

FN353

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

每股股东自由现金流

近一年营业利润(万元)

净利润（单季度）(万元)

北上资金数（家）(机构持股）

北上资金持股量（股）(机构持股）

有息负债率

营业成本（单季度）(万元)

投入资本回报率（ROIC）(获利能力分析)

业绩快报-营业收入（本期）

业绩快报-营业收入（上期）

业绩快报-营业利润（本期）

业绩快报-营业利润（上期）

业绩快报-利润总额（本期）

业绩快报-利润总额（上期）

审计意见 [注：0-未审计,1-无保留意见,2-带强调事项段的无保留意
见,3-保留意见,4-无法表示意见,5-否定意见及其他]

股利支付率（%）

近一年营业成本-非金融类(万元)

近一年营业成本-金融类(万元)

业绩预告-本期扣非后净利润下限(万元)

业绩预告-本期扣非后净利润上限(万元)

业绩预告-本期扣非后净利润同比增长下限（%）

业绩预告-本期扣非后净利润同比增长上限（%）

业绩预告-预告基本每股收益下限(元)

业绩预告-预告基本每股收益上限(元)

业绩预告-预告基本每股收益同比增长下限（%）

业绩预告-预告基本每股收益同比增长上限（%）

业绩预告-预告扣非后基本每股收益下限(元)

业绩预告-预告扣非后基本每股收益上限(元)

业绩预告-预告扣非后基本每股收益同比增长下限（%）

业绩预告-预告扣非后基本每股收益同比增长上限（%）

业绩预告-预告营业收入下限(万元)

业绩预告-预告营业收入上限(万元)

名称

 通达信量化平台

类型

数值

说明

FN354

FN355

FN356

FN357

FN358

FN359

FN360

FN361

FN362

FN401

FN402

FN403

FN404

FN405

FN406

FN407

FN408

FN409

FN410

FN411

FN412

FN413

FN414

FN415

FN416

FN417

FN418

FN419

FN420

FN421

FN422

FN423

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

业绩预告-预告营业收入同比增长下限（%）

业绩预告-预告营业收入同比增长上限（%）

业绩预告-预告扣除后营业收入下限(万元)

业绩预告-预告扣除后营业收入上限(万元)

主营业务收入(内销)(万元)

主营业务收入(外销)(万元)

资管计划机构数(家)

资管计划持股量(股)

财务总评分

专项储备(万元)

结算备付金(万元)

拆出资金(万元)

发放贷款及垫款(万元)(流动资产科目)

衍生金融资产(万元)

应收保费(万元)

应收分保账款(万元)

应收分保合同准备金(万元)

买入返售金融资产(万元)

划分为持有待售的资产(万元)

发放贷款及垫款(万元)(非流动资产科目)

向中央银行借款(万元)

吸收存款及同业存放(万元)

拆入资金(万元)

衍生金融负债(万元)

卖出回购金融资产款(万元)

应付手续费及佣金(万元)

应付分保账款(万元)

保险合同准备金(万元)

代理买卖证券款(万元)

代理承销证券款(万元)

划分为持有待售的负债(万元)

预计负债(万元) （流动负债）

名称

 通达信量化平台

类型

数值

说明

FN424

FN425

FN426

FN427

FN428

FN429

FN430

FN431

FN432

FN433

FN434

FN435

FN436

FN437

FN438

FN439

FN440

FN441

FN442

FN443

FN444

FN445

FN446

FN447

FN448

FN449

FN450

FN451

FN452

FN453

FN501

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

递延收益(万元)（流动负债科目，公告此科目的股票较少，大部分公
司没有此数据）

其中:优先股(万元)(非流动负债科目)

永续债(万元)(非流动负债科目)

长期应付职工薪酬(万元)

其中:优先股(万元)(所有者权益科目)

永续债(万元)(所有者权益科目)

债权投资(万元)

其他债权投资(万元)

其他权益工具投资(万元)

其他非流动金融资产(万元)

合同负债(万元)

合同资产(万元)

其他资产(万元)

应收款项融资(万元)

使用权资产(万元)

租赁负债(万元)

发放贷款及垫款(万元) [注：金融类科目]

应收款项(万元) [注：证券类指标]

存出保证金(万元) [注：证券类指标]

现金及存放中央银行款项(万元) [注：金融类科目]

贵金属(万元) [注：金融类科目]

以公允价值计量且其变动计入当期损益的金融资产(万元) [注：金融类
科目]

代理业务资产(万元) [注：金融类科目]

应收款项类投资(万元) [注：金融类科目]

同业及其它金融机构存放款项(万元) [注：金融类科目]

以公允价值计量且其变动计入当期损益的金融负债(万元) [注：金融类
科目]

吸收存款(万元) [注：金融类科目]

代理业务负债(万元) [注：金融类科目]

其他负债(万元) [注：金融类科目]

发放贷款及垫款(万元) [注：金融类科目]

稀释每股收益(元)

名称

 通达信量化平台

类型

数值

说明

FN502

FN503

FN504

FN505

FN506

FN507

FN508

FN509

FN510

FN511

FN512

FN513

FN514

FN515

FN516

FN517

FN518

FN519

FN520

FN521

FN522

FN523

FN524

FN561

FN562

FN563

FN564

FN565

FN566

FN567

FN568

FN569

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

营业总收入(万元)

汇兑收益(万元)

其中:归属于母公司综合收益(万元)

其中:归属于少数股东综合收益(万元)

利息收入(万元)

已赚保费(万元)

手续费及佣金收入(万元)

利息支出(万元)

手续费及佣金支出(万元)

退保金(万元)

赔付支出净额(万元)

提取保险合同准备金净额(万元)

保单红利支出(万元)

分保费用(万元)

其中:非流动资产处置利得(万元)

信用减值损失(万元)

净敞口套期收益(万元)

营业总成本(万元)

信用减值损失(万元、2019格式)

资产减值损失(万元、2019格式)

其他业务收入(万元) [注：金融类科目]

业务及管理费(万元) [注：金融类科目]

其他业务成本(万元) [注：金融类科目]

加:其他原因对现金的影响2(万元)(现金的期末余额科目)

客户存款和同业存放款项净增加额(万元)

向中央银行借款净增加额(万元)

向其他金融机构拆入资金净增加额(万元)

收到原保险合同保费取得的现金(万元)

收到再保险业务现金净额(万元)

保户储金及投资款净增加额(万元)

处置以公允价值计量且其变动计入当期损益的金融资产净增加额(万
元)

double

收取利息、手续费及佣金的现金(万元)

名称

 通达信量化平台

类型

数值

说明

FN570

FN571

FN572

FN573

FN574

FN575

FN576

FN577

FN578

FN579

FN580

FN581

FN582

FN583

FN584

double

double

double

double

double

double

double

double

double

double

double

double

double

double

double

拆入资金净增加额(万元)

回购业务资金净增加额(万元)

客户贷款及垫款净增加额(万元)

存放中央银行和同业款项净增加额(万元)

支付原保险合同赔付款项的现金(万元)

支付利息、手续费及佣金的现金(万元)

支付保单红利的现金(万元)

其中:子公司吸收少数股东投资收到的现金(万元)

其中:子公司支付给少数股东的股利、利润(万元)

投资性房地产的折旧及摊销(万元)

信用减值损失(万元)

使用权资产折旧（万元）

收取利息和手续费净增加额(万元) [注：金融类科目]

支付手续费的现金(万元) [注：金融类科目]

发行债券支付的现金(万元) [注：金融类科目]

返回值说明

返回类型： dict ，键为股票代码（如  '600519.SH' ），值为 pandas.DataFrame。

DataFrame 列：

用户请求的财务字段（如  FN193 ,  FN194  … 大写）。

announce_time ：公告日期，格式  YYYYMMDD 。

tag_time ：报告期截止日期，格式  YYYYMMDD 。

行：按时间顺序排列的财务数据记录。

接口使用

1

2

3

4

5

6

7

8

9

10

11

数据样本

1

2

from tqcenter import tq

tq.initialize(__file__)

fd = tq.get_financial_data(

        stock_list=['688318.SH'],

        field_list=['Fn193','Fn194','Fn195','Fn196','Fn197'],

        start_time='20250101',

        end_time='',

        report_type='announce_time')

print(fd)

{'600519.SH':     FN193  FN194  FN195 FN196  FN197 announce_time  tag_time

0  164.82  70.03  15.76  8.07  36.99      20250403  20241231

py

3

1  193.43  73.19  14.16  8.03  10.39      20250430  20250331

 通达信量化平台

4

2  166.69  70.22  15.60  8.70  19.02      20250813  20250630

5

3  162.47  69.67  16.07  8.71  25.14      20251030  20250930}

← 获取每天的股本数据get_gb_info

获取指定日期财务数据get_financial_data_by_date →

 通达信量化平台

获取指定日期专业财务数据get_financial_data_by_date

根据股票，获取指定日期的专业财务数据，与基础财务数据不同，需要先在客户端中下载专业财务数据

1

2

3

4

get_financial_data_by_date(stock_list: List[str] = [],

field_list: List[str] = [],

year: int = 0,

mmdd: int = 0) -> Dict:

是否必选

参数类型

参数说明

Y

Y

Y

Y

List[str]

证券代码列表

List[str]

字段筛选，不能为空（如  FN193 ）

int

int

指定年份

指定月日

输入参数

参数

stock_list

field_list

year

mmdd

输出参数

同get_financial_data一样。

接口使用

1

2

3

4

5

6

7

8

9

from tqcenter import tq

tq.initialize(__file__)

fd = tq.get_financial_data_by_date(

        stock_list=['688318.SH'],

        field_list=['Fn193','Fn194','Fn195','Fn196','Fn197'],

        year=0,

        mmdd=0)

10

print(fd)

数据样本

1

2

3

4

5

6

{'600519.SH':

{'FN193': '162.47',

'FN194': '69.67',

'FN195': '16.07',

'FN196': '8.71',

'FN197': '25.14'}}

py

py

 通达信量化平台

← 获取专业财务数据get_financial_data

获取股票交易数据get_gpjy_value →

 通达信量化平台

获取股票交易数据get_gpjy_value

根据股票，获取指定时间段内的股票交易数据，需要先在客户端中下载股票数据包

1

2

3

4

get_gpjy_value(stock_list: List[str] = [],

field_list: List[str] = [],

start_time: str = '',

end_time: str = '') -> Dict:

py

输入参数

参数

stock_list

field_list

start_time

end_time

输出参数

是否必选

参数类型

参数说明

Y

Y

N

N

List[str]

证券代码列表

List[str]

字段筛选，不能为空

str

str

起始时间

结束时间

名称

类型

数值

说明

GP01

double

股东人数 股东户数(户)

GP02

double

龙虎榜 买入总计(万元) 卖出总计(万元)[注：该指标展示20230717日之后的数据]

GP03

double

融资融券1 融资余额(万元) 融券余量(股)

GP04

double

大宗交易 成交均价(元) 成交额(万元)

GP05

double

增减持1 成交均价(元) 变动股数(股)

GP06

double

陆股通持股量 持股数量(股)[注：该指标展示20170317日之后的数据]

GP07

double

陆股通市场成交净额 陆股通市场净买入(万元)[注：官方只公布了每日的前十名数据]

GP08

double

龙虎榜机构(卖方)数据 卖方机构个数 机构卖出金额(万元)

GP09

double

龙虎榜机构(买方)数据 买方机构个数 机构买入金额(万元)

GP10

double

近3月机构调研情况 近3月机构调研次数 近3月调研机构数量

GP11

double

融资融券2 融资买入额(万元) 融资偿还额(万元)

GP12

double

融资融券3 融券卖出量(股) 融券偿还量(股)

GP13

double

融资融券4 融资净买入(万元) 融券净卖出(股)

GP14

double

涨停数据 涨停金额(即板上成交,万元) 开板次数[注：该指标展示20180319日之后的数据]

GP15

double

涨跌停 涨跌停状态 封单金额(万元)[注：涨停取2,曾涨停取1,跌停取-2,曾跌停取-1;跌停和曾跌
停时,封单金额取负值 该指标展示20160926日之后的数据]

GP16

double

总市值 总市值(万元)

类型
 通达信量化平台

名称

数值

说明

GP17

double

龙虎榜营业部数据 买入金额(万元) 卖出金额(万元)

GP18

double

龙虎榜沪深股通数据 买入金额(万元) 卖出金额(万元)

GP19

double

每周股票质押数量 无限售股份质押数(万) 有限售股份质押数(万)[注：该指标展示20180316日
之后的数据]

GP20

double

每周股票质押比例 质押比例(%)[注：该指标展示20180316日之后的数据]

GP21

double

股息率 股息率(%)

GP22

double

涨跌停 封成比 封流比[注：该指标展示20180319日之后的数据]

GP23

double

拟增减持 拟增持数量(万股) 拟减持数量(万股)

GP24

double

GP25

double

涨停 首次涨停时间 涨停最大封单额(万) [注：首次涨停时间展示20160301之后的数据，涨停
最大封单额展示20200730之后的数据]

盘前盘后成交量 开盘成交量(手) 盘后固定成交量(手) [注：盘后固定成交量只包含科创板和创
业板]

GP26

double

拟增减持金额 拟增持金额(万元) 拟减持金额(万元)

GP27

double

人气排名 市场人气排名 行业人气排名 [注：行业排名为通达信二级研究行业排名]

GP28

double

股票回购 回购均价(元) 回购数量(万股)

GP29

double

证券信息 是否复牌日 是否更名日 [注：是否复牌日说明：0-不是复牌日，n(n>0)-停牌n个交
易日之后的复牌日；是否更名日说明：0-未更名，1-常规更名，2-加ST，3-加*ST，4-摘帽，
5-其他]

GP30

double

分红送转 派息金额(万元) 送转数量(股) [注：对应展示日期为除权除息日]

GP31

double

转融券 期初余量(股) 期末余量(股)

GP32

double

转融券 融出数量(股) 融出市值(元)

GP33

double

GP34

double

跌停数据 跌停金额(万元) 开板次数 [注：该指标展示20180319日之后的数据,暂无跌停金额数
据]

跌停 首次跌停时间 跌停最大封单额(万) [注：首次跌停时间展示20160301之后的数据，跌停
最大封单额展示20200730之后的数据]

GP35

double

增减持2 增持数量(股) 减持数量(股)

GP36

double

竞价涨停买 买入金额(万元) [注：该指标展示20241101日之后的数据]

GP37

double

龙虎榜2 上榜类型连续交易日(天) [注：该指标展示上榜类型中指代的连续交易日类型]

GP38

double

涨停相关1 近1年涨停次数 近1年溢价5%次数

GP39

double

涨停相关2 近1年首板封板率(%) 近1年次日红盘率(%)

GP40

double

涨停相关3 近1年连板率(%) 最后涨停时间

GP41

double

股权登记日 配股股权登记日

GP42

double

龙虎榜专业机构买卖净额 买方成交净额(万元) 卖方成交净额(万元)

GP43

double

配股实施 配股价格(元) 配股数量(万股)

GP44

double

股票评分 综合评分

GP45

double

评级系数 评级系数

类型
 通达信量化平台

名称

数值

说明

GP46

double

拟询价转让 拟转让股数(万股) 拟转让占总股本(%)

接口使用

1

2

3

4

5

6

7

8

9

from tqcenter import tq

tq.initialize(__file__)

gp_val = tq.get_gpjy_value(

        stock_list=['688318.SH'],

        field_list=['GP1','GP2','GP3','GP4','GP5'],

        start_time='20250101',

        end_time='20250102')

10

print(gp_val)

数据样本

1

{'688318.SH': {'GP3': [{'Date': '20250102', 'Value': ['141405.89', '11113.00']}]}}

py

← 获取指定日期财务数据get_financial_data_by_date

获取指定日期股票交易数据get_gpjy_value_by_date →

 通达信量化平台

获取指定日期股票交易数据get_gpjy_value_by_date

根据股票，获取指定时间段内的股票交易数据，需要先在客户端中下载股票数据包

1

2

3

4

def get_gpjy_value_by_date(stock_list: List[str] = [],

field_list: List[str] = [],

year: int = 0,

mmdd: int = 0) -> Dict:

输入参数

参数

stock_list

field_list

year

mmdd

是否必选

参数类型

参数说明

Y

Y

Y

Y

List[str]

证券代码列表

List[str]

字段筛选，不能为空

int

int

指定年份

指定月日

当year和mmdd默认为0时返回最近一条数据。

输出参数

同get_gpjy_value一样。

接口使用

from tqcenter import tq

tq.initialize(__file__)

gp_one = tq.get_gpjy_value_by_date(

        stock_list=['688318.SH'],

        field_list=['GP1','GP2','GP3','GP4','GP5'],

        year=0,mmdd=0)

print(gp_one)

1

2

3

4

5

6

7

8

9

数据样本

py

py

1

{'688318.SH': {'GP1': ['24154.00', '0.00'], 'GP2': ['20574.12', '18728.85'], 'GP3': ['140464.83', '55043.00'],

← 获取股票交易数据get_gpjy_value

获取板块交易数据get_bkjy_value →

 通达信量化平台

获取板块交易数据get_bkjy_value

根据板块代码，获取指定时间段内的板块交易数据，需要先在客户端中下载股票数据包

1

2

3

4

get_bkjy_value(stock_list: List[str] = [],

field_list: List[str] = [],

start_time: str = '',

end_time: str = '') -> Dict:

py

输入参数

参数

stock_list

field_list

start_time

end_time

输出参数

是否必选

参数类型

参数说明

Y

Y

N

N

List[str]

证券代码列表

List[str]

字段筛选，不能为空

str

str

起始时间

结束时间

名称

类型

数值

说明

BK5

double

市盈率TTM 整体法 算术平均

BK6

double

市净率MRQ 整体法 算术平均

BK7

double

市销率TTM 整体法 算术平均

BK8

double

市现率TTM 整体法 算术平均

BK9

double

涨跌数 上涨家数 下跌家数

BK10

double

板块总市值(亿元) 整体法 算术平均

BK11

double

板块流通市值(亿元) 整体法 算术平均

BK12

double

涨停数 涨停家数 曾涨停家数[注：该指标展示20160926日之后的数据]

BK13

double

跌停数 跌停家数 曾跌停家数[注：该指标展示20160926日之后的数据]

BK14

double

涨停数据 市场高度(不含ST股和未开板新股) 2板及以上涨停个数(不含ST股和未开板新股)
[注：该指标展示20180319日之后的数据]

BK15

double

融资融券 沪深京融资余额(万元) 沪深京融券余额(万元)

BK16

double

陆股通资金流入 沪股通流入金额(亿元) 深股通流入金额(亿元) [注：该指标展示20170320日
之后的数据]

BK17

double

开盘成交数 开盘成交额(万元) 开盘成交量(万股)

BK18

double

板块股息率(%) 算数平均 整体法

BK19

double

板块自由流通市值(亿元) 整体法 算术平均

 通达信量化平台

接口使用

1

2

3

4

5

6

7

8

9

数据样本

1

2

3

4

5

from tqcenter import tq

tq.initialize(__file__)

bk_data = tq.get_bkjy_value(stock_list=['880660.SH'],

        field_list=['BK5','BK6','BK7','BK8','BK9'],

        start_time='20250101',

        end_time='20250102')

print(bk_data)

py

{'880660.SH': {'BK5': [{'Date': '20250102', 'Value': ['55.28', '55.50']}],

'BK6': [{'Date': '20250102', 'Value': ['4.62', '3.79']}],

'BK7': [{'Date': '20250102', 'Value': ['5.25', '8.22']}],

'BK8': [{'Date': '20250102', 'Value': ['46.52', '312.41']}],

'BK9': [{'Date': '20250102', 'Value': ['0.00', '35.00']}, {'Date': '20260130', 'Value': ['10.00', '25.00']}]}}

← 获取指定日期股票交易数据get_gpjy_value_by_date

获取指定日期板块交易数据get_bkjy_value_by_date →

 通达信量化平台

获取指定日期板块交易数据get_bkjy_value_by_date

根据板块代码，获取指定日期的板块交易数据，需要先在客户端中下载股票数据包

1

2

3

4

get_bkjy_value_by_date(stock_list: List[str] = [],

field_list: List[str] = [],

year: int = 0,

mmdd: int = 0) -> Dict:

输入参数

参数

stock_list

field_list

year

mmdd

是否必选

参数类型

参数说明

Y

Y

Y

Y

List[str]

证券代码列表

List[str]

字段筛选，不能为空

int

int

指定年份

指定月日

当year和mmdd默认为0时返回最近一条数据。

输出参数

同get_bkjy_value一样。

接口使用

from tqcenter import tq

tq.initialize(__file__)

bk_one = tq.get_bkjy_value_by_date(stock_list=['880660.SH'],

                                   field_list=['BK9','BK10','BK11','BK12','BK13'],

                                   year=0,mmdd=0)

print(bk_one)

1

2

3

4

5

6

7

8

数据样本

py

py

1

{'880660.SH': {'BK10': ['6705.83', '191.60'], 'BK11': ['6183.65', '176.68'], 'BK12': ['0.00', '0.00'], 'BK13':

← 获取板块交易数据get_bkjy_value

获取市场交易数据get_scjy_value →

 通达信量化平台

获取市场交易数据

获取指定时间段内的市场交易数据，需要先在客户端中下载股票数据包

1

2

3

get_scjy_value(field_list: List[str] = [],

start_time: str = '',

end_time: str = '') -> Dict:

py

输入参数

参数

field_list

start_time

end_time

输出参数

是否必选

参数类型

参数说明

Y

N

N

List[str]

字段筛选，不能为空

str

str

起始时间

结束时间

名称

类型

数值

说明

SC01

double

融资融券 沪深京融资余额(万元) 沪深京融券余额(万元)

SC02

double

陆股通资金流入 沪股通流入金额(亿元) 深股通流入金额(亿元)[注：沪股通限制展示2000条数
据，深股通展示自20161205以后的数据]

SC03

double

沪深京涨停股个数 涨停股个数 曾涨停股个数 [注：该指标展示20160926日之后的数据]

SC04

double

沪深京跌停股个数 跌停股个数 曾跌停股个数 [注：该指标展示20160926日之后的数据]

SC05

double

上证50股指期货 净持仓(手)[注：该指标展示20171009日之后的数据]

SC06

double

沪深300股指期货 净持仓(手) [注：该指标展示20171009日之后的数据]

SC07

double

中证500股指期货 净持仓(手) [注：该指标展示20171009日之后的数据]

SC08

double

ETF基金规模份额数据 ETF基金规模(亿份) ETF净申赎(亿份)

SC09

double

沪月新开A股账户 沪月新开A股账户(万户)

SC10

double

增减持统计 增持额(万元) 减持额(万元)[注：部分公司公告滞后,造成每天查看的数据可能会不
一样]

SC11

double

大宗交易 溢价的大宗交易额(万元) 折价的大宗交易额(万元)

SC12

double

限售解禁 限售解禁计划额(亿元) 限售解禁股份实际上市金额(亿元)[注：该指标展示201802月
之后的数据;部分股票的解禁日期延后，造成不同日期提取的某天的计划额可能不同]

SC13

double

分红 市场总分红额(亿元)[注：除权派息日的A股市场总分红额]

SC14

double

募资 市场总募资额(亿元)[注：发行日期/除权日期的首发、配股和增发的总募资额]

SC15

double

打板资金 封板成功资金(亿元) 封板失败资金(亿元) [注：该指标展示20160926日之后的数据]

SC16

double

龙虎榜 买入总金额(亿元) 卖出总金额(亿元)

类型
 通达信量化平台

名称

数值

说明

SC17

double

龙虎榜机构数据 买入金额(亿元) 卖出金额(亿元)

SC18

double

龙虎榜营业部数据 买入金额(亿元) 卖出金额(亿元)

SC19

double

龙虎榜沪深股通数据 买入金额(亿元) 卖出金额(亿元)

SC20

double

陆股通净买入 沪股通净买入额(亿元) 深股通净买入额(亿元)

SC21

double

每周无限售质押率 深市质押率(%) 沪市质押率(%)[注：该指标展示20180128日之后的数据]

SC22

double

每周有限售质押率 深市质押率(%) 沪市质押率(%)[注：该指标展示20180128日之后的数据]

SC23

double

SC24

double

连板家数 连板股个数(包含ST和未开板新股) 连板股个数(不含ST股和未开板新股）[注：该指
标展示20180319日之后的数据]

沪深京涨跌停股个数 涨停股个数(不含ST股和未开板新股) 跌停股个数（不含ST股）[注：该指
标展示20160926日之后的数据]

SC25

double

融资融券 沪深京融资买入额（万元）沪深京融券卖出量（万股）

SC26

double

每周市场质押比 每周市场质押比例（%）[注：该指标展示20180316日之后的数据]

SC27

double

央行公开市场净投放 央行公开市场净投放 (亿元)

SC28

double

历史A股新高新低数 历史新高A股股票个数 历史新低A股股票个数(上市满一年的股票)

SC29

double

120天A股新高新低数 120天新高A股股票个数 120天新低A股股票个数(上市满一年的股票)

SC30

double

涨停数据 市场高度(不含ST股和未开板新股) 2板以上涨停个数(不含ST股和未开板新股)[注：
该指标展示20180319日之后的数据]

SC31

double

涨跌家数 涨家数（剔除停牌） 跌家数（剔除停牌）

SC32

double

20天A股新高新低数 20天新高A股股票个数 20天新低A股股票个数(上市满一年的股票)

SC33

double

市场总封单金额 涨停封单金额（亿元）跌停封单金额（亿元）[注：该指标展示20160926日
之后的数据]

SC34

double

涨跌股成交量 上涨股成交量(万手) 下跌股成交量(万手)

SC35

double

SC36

double

涨停数据 换手板家数 回封率(%) [注：两个指标都剔除了未开板新股，换手板家数展示
20190605日之后的数据，回封率展示20180927日之后的数据]

曾涨跌停股个数 曾涨停股个数(剔除ST股和未开板新股) 曾跌停股个数(剔除ST股) [注：该指标
展示20160926日之后的数据]

SC37

double

转融券 融出市值(亿元) 期末余额(亿元)

SC38

double

ETF基金规模金额数据 ETF基金规模(亿元) ETF净申赎(亿元)

SC39

double

涨跌5%家数 涨幅大于等于5%家数 跌幅大于等于5%家数

SC40

double

陆股通成交 陆股通成交总额(亿元) 陆股通成交总笔(万笔)

SC41

double

中证1000股指期货 净持仓(手) [注：该指标展示20220722日之后的数据]

SC42

double

沪深股通成交金额 沪股通成交总额(亿元) 深股通成交总额(亿元)

接口使用

1

2

3

from tqcenter import tq

tq.initialize(__file__)

py

4

 通达信量化平台

5

sc_val = tq.get_scjy_value(field_list=['SC1','SC2','SC3','SC4','SC5'],

6

7

数据样本

1

2

3

4

5

        start_time='20250101',end_time='20250102')

print(sc_val)

{'SC1': [{'Date': '20250102', 'Value': ['184712288.00', '999820.06']}],

'SC2': [{'Date': '20250102', 'Value': ['0.00', '0.00']}],

'SC3': [{'Date': '20250102', 'Value': ['67.00', '49.00']}],

'SC4': [{'Date': '20250102', 'Value': ['32.00', '30.00']}],

'SC5': [{'Date': '20250102', 'Value': ['-21204.00', '0.00']}]}

← 获取指定日期板块交易数据get_bkjy_value_by_date

获取指定日期市场交易数据get_scjy_value_by_date →

 通达信量化平台

获取指定日期市场交易数据get_scjy_value_by_date

获取指定时间的市场交易数据，需要先在客户端中下载股票数据包

1

2

3

get_scjy_value_by_date(field_list: List[str] = [],

year: int = 0,

mmdd: int = 0) -> Dict:

输入参数

参数

field_list

year

mmdd

是否必选

参数类型

参数说明

Y

Y

Y

List[str]

字段筛选，不能为空

int

int

指定年份

指定月日

当year和mmdd默认为0时返回最近一条数据。

输出参数

同get_scjy_value一样。

接口使用

py

py

from tqcenter import tq

tq.initialize(__file__)

sc_one = tq.get_scjy_value_by_date(field_list=['SC6','SC7','SC8','SC9','SC10'],year=0,mmdd=0)

print(sc_one)

1

2

3

4

5

6

数据样本

1

{'SC10': ['0.00', '181415.13'], 'SC6': ['-30479.00', '0.00'], 'SC7': ['-26449.00', '0.00'], 'SC8': ['31752.86',

← 获取市场交易数据get_scjy_value

获取股票的单个数据(非序列)get_gp_one_data →

 通达信量化平台

获取股票的单个财务数据get_gp_one_data

根据证券代码，获取股票的单个数据，需要先在客户端中下载股票数据包

1

2

get_gp_one_data(stock_list: List[str] = [],

field_list: List[str] = []) -> Dict:

py

输入参数

参数

stock_list

field_list

输出参数

是否必选

参数类型

参数说明

Y

Y

List[str]

证券代码列表

List[str]

字段筛选，不能为空（如  GO47 表示是第47号个股数据最新业
绩预告 本期扣非净利润预计同比增减幅上限%）这个值，GO
为gp one的首字母大写

名称

类型

数值

说明

GO1

double

发行价(元)

GO2

double

总发行数量(万股)

GO3

double

一致预期目标价(元)[注：一致预期值均为近半年内各家机构预测数值的平均值]

GO4

double

一致预期T年度

GO5

double

一致预期T年每股收益

GO6

double

一致预期T+1年每股收益

GO7

double

一致预期T+2年每股收益

GO8

double

一致预期T年净利润(万元)

GO9

double

一致预期T+1年净利润(万元)

GO10

double

一致预期T+2年净利润(万元)

GO11

double

一致预期T年营业收入(万元)

GO12

double

一致预期T+1年营业收入(万元)

GO13

double

一致预期T+2年营业收入(万元)

GO14

double

一致预期T年营业利润(万元)

GO15

double

一致预期T+1年营业利润(万元)

GO16

double

一致预期T+2年营业利润(万元)

GO17

double

一致预期T年每股净资产(元)

GO18

double

一致预期T+1年每股净资产(元)

类型
 通达信量化平台

名称

数值

说明

GO19

double

一致预期T+2年每股净资产(元)

GO20

double

一致预期T年净资产收益率(%)

GO21

double

一致预期T+1年净资产收益率(%)

GO22

double

一致预期T+2年净资产收益率(%)

GO23

double

一致预期T年PE

GO24

double

一致预期T+1年PE

GO25

double

一致预期T+2年PE

GO26

double

最新解禁日(YYMMDD格式)

GO27

double

最新解禁数量（万股）

GO28

double

下一报告期的预约披露时间

GO29

double

最新持股机构家数

GO30

double

最新机构持股总量（万股）

GO31

double

最新持股基金家数

GO32

double

最新基金持股量（万股）

GO33

double

最新总股本（万股）

GO34

double

最新实际流通A股（万股）

GO35

double

最新业绩预告 报告期(YYMMDD格式)

GO36

double

最新业绩预告 本期归母净利润下限（万元）

GO37

double

最新业绩预告 本期归母净利润上限（万元）

GO38

double

最新业绩预告 本期归母净利润预计同比增减幅下限%

GO39

double

最新业绩预告 本期归母净利润预计同比增减幅上限%

GO40

double

最新业绩快报 报告期

GO41

double

最新业绩快报 归母净利润（万元）

GO42

double

分红募资 派现总额（万元）

GO43

double

分红募资 募资总额（万元）

GO44

double

最新业绩预告 本期扣非净利润下限(万元)

GO45

double

最新业绩预告 本期扣非净利润上限(万元)

GO46

double

最新业绩预告 本期扣非净利润预计同比增减幅下限%

GO47

double

最新业绩预告 本期扣非净利润预计同比增减幅上限%

接口使用

1

2

3

from tqcenter import tq

tq.initialize(__file__)

py

4

 通达信量化平台

5

go = tq.get_gp_one_data(stock_list=['688318.SH'],field_list=['GO1','GO2','GO3','GO4','GO5'])

6

print(go)

数据样本

1

{'688318.SH': {'GO1': '107.41', 'GO2': '1667.00', 'GO3': '0.00', 'GO4': '2025.00', 'GO5': '1.74'}}

← 获取指定日期市场交易数据get_scjy_value_by_date

获取系统分类成份股get_stock_list →

 通达信量化平台

获取A股板块代码列表get_sector_list

获取A股全部板块代码列表

1

def get_sector_list(list_type: int = 0) -> List:

输入参数

参数

是否必选

参数类型

参数说明

list_type

Y

int

返回数据类型

list_type = 0 只返回代码，list_type = 1 返回代码和名称

接口使用

1

2

3

4

5

6

from tqcenter import tq

tq.initialize(__file__)

block_list = tq.get_sector_list()

print(block_list)

block_list2 = tq.get_sector_list(list_type = 1)

print(block_list2)

注：此接口相当于 get_stock_list('10')

py

py

数据样本

1

2

3

['880081.SH', '880082.SH', '880201.SH', '880202.SH', '880203.SH', '880204.SH', '880205.SH', '880206.SH', '88020

[{'Code': '880081.SH', 'Name': '轮动趋势'}, {'Code': '880082.SH', 'Name': '板块趋势'}, {'Code': '880201.SH', 'Nam

← 获取系统分类成份股get_stock_list

获取板块成份股get_stock_list_in_sector →

 通达信量化平台

获取系统分类成份股get_stock_list

根据入参返回指定证券代码列表

1

2

    def get_stock_list(market = None,

                       list_type: int = 0) -> List:

py

输入参数

参数

是否必选

参数类型

参数说明

market

list_type

Y

Y

str

int

指定代码

返回数据类型

list_type = 0 只返回代码，list_type = 1 返回代码和名称

1

2

3

4

5

6

7

8

接口使用

1

2

3

4

5

6

7

数据样本

1

2

3

默认为全部A股

    0:自选股 1:持仓股

    5:所有A股 6:上证指数成份股 7:上证主板 8:深证主板 9:重点指数

    10:所有板块指数 11:缺省行业板块 12:概念板块 13:风格板块 14:地区板块 15:缺省行业分类+概念板块 16:研究行业一级 17:研究

    21:含H股 22:含可转债 23:沪深300 24:中证500 25:中证1000 26:国证2000 27:中证2000 28:中证A500

    30:REITs 31:ETF基金 32:可转债 33:LOF基金 34:所有可交易基金 35:所有沪深基金 36:T+0基金

    49:金融类企业 50:沪深A股 51:创业板 52:科创板 53:北交所

    101:国内期货 102:港股 103:美股

from tqcenter import tq

tq.initialize(__file__)

stock_list = tq.get_stock_list('16')

print(stock_list)

stock_list2 = tq.get_stock_list('16',list_type=1)

print(stock_list2)

py

['881001.SH', '881006.SH', '881015.SH', '881061.SH', '881070.SH', '881090.SH', '881105.SH', '881129.SH', '88115

[{'Code': '881001.SH', 'Name': '煤炭'}, {'Code': '881006.SH', 'Name': '石油'}, {'Code': '881015.SH', 'Name': '化

← 获取股票的单个数据(非序列)get_gp_one_data

获取A股板块代码列表get_sector_list →

py

py

 通达信量化平台

获取板块成份股get_stock_list_in_sector

根据板块代码获取其成份股列表

1

2

3

def get_stock_list_in_sector(block_code: str,

                         block_type: int = 0,

                         list_type: int = 0) -> List:

输入参数

参数

block_code

block_type

list_type

是否必选

参数类型

参数说明

Y

N

Y

str

str

int

板块代码

板块类型

返回数据类型

获取A股成份股时支持板块名称或板块代码两种方式传入

block_type=0 表示传入板块代码或名称（默认）

block_type=1 表示传入自定义板块简称 需要是客户端中预先定义好板块简称 不能是 自选股 或 临时条件股

list_type = 0 只返回代码，list_type = 1 返回代码和名称

from tqcenter import tq

tq.initialize(__file__)

#通过板块代码获取成份股

block_stocks = tq.get_stock_list_in_sector('880081.SH')

print(block_stocks)

print(len(block_stocks))

#通过板块名获取成份股

block_stocks = tq.get_stock_list_in_sector('钛金属')

print(block_stocks)

print(len(block_stocks))

block_stocks2 = tq.get_stock_list_in_sector('钛金属',list_type=1)

print(block_stocks2)

#获取自定义板块成份股

block_stocks = tq.get_stock_list_in_sector('CSBK', block_type = 1)

print(block_stocks)

print(len(block_stocks))

接口使用

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

数据样本

1

2

3

4

5

['159922.SZ', '510500.SH', '512500.SH']

3

['000545.SZ', '000629.SZ', '000635.SZ', '000688.SZ', '000709.SZ', '000962.SZ', '002136.SZ', '002140.SZ', '00214

23

[{'Code': '000545.SZ', 'Name': '金浦钛业'}, {'Code': '000629.SZ', 'Name': '钒钛股份'}, {'Code': '000635.SZ', 'Nam

6

['600000.SH', '600004.SH', '600006.SH', '600007.SH', '600008.SH', '600009.SH', '600010.SH']

 通达信量化平台

7

7

注意

get_stock_list_in_sector 入参的板块只能是自定义板块或者15板块指数

不支持系统 全部A股 沪深A股等板块

← 获取A股板块代码列表get_sector_list

获取自定义板块列表get_user_sector →

 通达信量化平台

获取自定义板块列表get_user_sector

获取自定义板块代码列表

1

get_user_sector(cls) -> List:

接口使用

1

2

3

4

5

from tqcenter import tq

tq.initialize(__file__)

user_list = tq.get_user_sector()

print(user_list)

print(len(user_list))

数据样本

py

py

1

[{'Code': 'CSBK', 'Name': '测试板块'}, {'Code': 'CSBK2', 'Name': '测试板块2'}]

← 获取板块成份股get_stock_list_in_sector

添加自定义板块成份股send_user_block →

 通达信量化平台

创建自定义板块

在通达信客户端中创建自定义板块

1

2

create_sector(block_code:str = '',

block_name:str = ''):

输入参数

参数

block_code

block_name

接口使用

是否必选

参数类型

参数说明

Y

Y

str

str

自定义板块简称

自定义板块名称

from tqcenter import tq

tq.initialize(__file__)

create_ptr = tq.create_sector(block_code='CSBK2', block_name='测试板块2')

print(create_ptr)

1

2

3

4

数据样本

1

2

3

4

5

{

   "Error" : "创建CSBK2板块成功",

   "ErrorId" : "0",

   "run_id" : "1"

}

py

py

← 清空自定义板块成份股clear_sector

删除自定义板块delete_sector →

 通达信量化平台

删除自定义板块

删除通达信客户端中的自定义板块

1

delete_sector(block_code:str = ''):

输入参数

参数

是否必选

参数类型

参数说明

block_code

Y

str

自定义板块简称

from tqcenter import tq

tq.initialize(__file__)

delete_ptr = tq.delete_sector(block_code='CSBK')

print(delete_ptr)

接口使用

1

2

3

4

数据样本

1

2

3

4

5

{

   "Error" : "删除CSBK板块成功",

   "ErrorId" : "0",

   "run_id" : "1"

}

py

py

← 创建自定义板块create_sector

重命名自定义板块rename_sector →

 通达信量化平台

创建自定义板块

重命名通达信客户端中的自定义板块

1

2

rename_sector(block_code:str = '',

block_name:str = ''):

输入参数

参数

block_code

block_name

接口使用

是否必选

参数类型

参数说明

Y

Y

str

str

自定义板块简称

重命名后的自定义板块名称

from tqcenter import tq

tq.initialize(__file__)

rename_ptr = tq.rename_sector(block_code='CSBK', block_name='测试板块重命名')

print(rename_ptr)

1

2

3

4

数据样本

1

2

3

4

5

{

   "Error" : "重命名CSBK板块成功",

   "ErrorId" : "0",

   "run_id" : "1"

}

py

py

← 删除自定义板块delete_sector

可转债基础信息get_cb_info →

 通达信量化平台

添加自定义板块成份股

往指定自定义板块中添加成份股

1

2

3

send_user_block(block_code: str = '',

                stocks: List[str] = [],

                show: bool = False) -> Dict:

输入参数

参数

block_code

stocks

show

是否必选

参数类型

参数说明

Y

Y

N

str

自定义板块简称

List[str]

添加的自选股

str

客户端是否切换至对应板块界面

block_code 为客户端已有的自定义板块简称，如果不存在则无效果，空则为添加到临时条件股

block_code存在，传入空列表则表示清空该板块所有股票，否则为添加新股票

自选股的block_code为ZXG

from tqcenter import tq

tq.initialize(__file__)

zxg_result = tq.send_user_block(block_code='CSBK', stocks=["600000.SH","600004.SH","000001.SZ","000002.SZ"])

接口使用

1

2

3

数据样本

1

{'Error': 'Add User Block Completed', 'ErrorId': '0', 'run_id': '1'}

← 获取自定义板块列表get_user_sector

清空自定义板块成份股clear_sector →

py

py

 通达信量化平台

清空自定义板块成份股

清空指定通达信客户端自定义板块的成份股

1

clear_sector(block_code:str = ''):

输入参数

参数

是否必选

参数类型

参数说明

block_code

Y

str

自定义板块简称

from tqcenter import tq

tq.initialize(__file__)

clear_ptr = tq.clear_sector(block_code='CSBK')

print(clear_ptr)

接口使用

1

2

3

4

数据样本

1

2

3

4

5

{

   "Error" : "清空CSBK板块成功",

   "ErrorId" : "0",

   "run_id" : "1"

}

py

py

← 添加自定义板块成份股send_user_block

创建自定义板块create_sector →

 通达信量化平台

获取可转债基础信息get_cb_info

根据可转债代码获取可转债基础信息

1

2

def get_cb_info(stock_code:str = '',

field_list: List[str] = []):

输入参数

参数

stock_code

field_list

接口使用

是否必选

参数类型

参数说明

Y

N

str

可转债代码

List[str]

字段筛选，传空则返回全部

from tqcenter import tq

tq.initialize(__file__)

cb_info = tq.get_cb_info(stock_code = '123039.SZ')

print(cb_info)

1

2

3

4

数据样本

py

py

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

{'CurRate': '2.80',

'EndDate': '20251226',

'EndPrice': '115.00',

'ExpireYield': '0.00',

'ForceRedeem': '37.90',

'HSCode': '300577',

'HSScore': 'A+',

'KZZCode': '123039',

'KZZScore': 'A+',

'PutBack': '20.41',

'PutDate': '0',

'PutPrice': '0.00',

'RealValue': '0.00',

'RedeemDate': '0',

'RedeemPrice': '0.00',

'RestScope': '22044.02',

'ZGCode': '123039',

'ZGDate': '20200702',

'ZGPrice': '29.15',

'ZGRate': '1.15',

'setcode': '0'}

← 重命名自定义板块rename_sector

期货品种基本信息 product_basic暂未开放 →

 通达信量化平台

 通达信量化平台

期货品种基本信息 product_basic暂未开放

← 可转债基础信息get_cb_info

合约详细信息 future_basic暂未开放 →

 通达信量化平台

合约详细信息 future_basic暂未开放

← 期货品种基本信息 product_basic暂未开放

格式化K线数据formula_format_data →

 通达信量化平台

格式化K线数据formula_format_data

格式化get_market_data获取的K线数据

1

    def formula_format_data(data_dict: Dict = {}):

py

输入参数

参数

是否必选

参数类型

参数说明

data_dict

Y

Dict

get_market_data获取格式的K线Dict

get_market_data获取的K线数据不能直接用于设置公式参数，须先调用formula_format_data进行格式化

formula_format_data返回值为List[Dict]，其中Dict的Key须有["Amount", "Volume", "Close", "Open", "High", "Low"]，用户可以

直接提供符合条件的List提供给tdx_formula_set_data。

接口使用

1

2

3

4

5

6

7

数据样本

1

2

3

4

5

6

from tqcenter import tq

tq.initialize(__file__)

test_md = tq.get_market_data(stock_list=['688318.SH'], count=5, period='1d')

format_md = tq.formula_format_data(test_md)

print(format_md)

py

{'688318.SH': [

{'Date': '2026-01-20 00:00:00', 'Amount': 33930.29, 'Volume': 2345401.0, 'Close': 144.4, 'Open': 146.5, 'High':

{'Date': '2026-01-21 00:00:00', 'Amount': 35841.09, 'Volume': 2472760.0, 'Close': 144.77, 'Open': 144.49, 'High

{'Date': '2026-01-22 00:00:00', 'Amount': 41598.79, 'Volume': 2878793.0, 'Close': 143.03, 'Open': 145.0, 'High'

{'Date': '2026-01-23 00:00:00', 'Amount': 47131.04, 'Volume': 3256538.0, 'Close': 144.39, 'Open': 142.58, 'High

{'Date': '2026-01-26 00:00:00', 'Amount': 54141.73, 'Volume': 3761141.0, 'Close': 141.84, 'Open': 143.7, 'High'

← 合约详细信息 future_basic暂未开放

向通达信公式设置数据formula_set_data →

 通达信量化平台

向通达信公式设置数据formula_set_data

在调用公式前须先设置公式参数，此接口与formula_set_data_info作用一样，会互相覆盖

1

2

3

4

5

    def formula_set_data(stock_code: str = '',

                    stock_period: str = '1d',

                    stock_data: List = [],

                    count: int = 1,

                    dividend_type: int = 0):

输入参数

参数

stock_code

stock_period

stock_data

count

dividend_type

是否必选

参数类型

参数说明

Y

Y

Y

Y

Y

str

str

List

int

int

股票代码

K线周期

指定格式的K线数据

选取的K线数量

复权类型

dividend_type的取值为：0不复权 1前复权 2后复权

count为设定stock_data中生效的K线数据，即stock_data中有效数据不能小于count

count须大于0，且最大不超过24000

设置的数据在断开连接前一直生效，后设置的数据会覆盖前面设置的数据

from tqcenter import tq

tq.initialize(__file__)

接口使用

1

2

3

4

5

6

7

8

数据样本

test_md = tq.get_market_data(stock_list=['688318.SH'], count=5, period='1d')

format_md = tq.tdx_formula_format_data(test_md)

formula_set_k = tq.formula_set_data(stock_code='688318.SH', stock_period='1d', stock_data=format_md['688318.SH'

print(formula_set_k)

1

{'ErrorId': '0', 'Msg': '向通达信公式系统设置数据成功！', 'run_id': '1'}

← 格式化K线数据formula_format_data

向通达信公式设置数据信息formula_set_data_info →

py

py

 通达信量化平台

向通达信公式设置数据信息formula_set_data_info

在调用公式前须先设置公式参数，此接口与formula_set_data作用一样，会互相覆盖

1

2

3

4

5

6

    def formula_set_data_info(stock_code: str = '',

                    stock_period: str = '1d',

                    start_time: str = '',

                    end_time: str = '',

                    count: int = -1,

                    dividend_type: int = 0):

输入参数

参数

stock_code

stock_period

start_time

end_time

count

dividend_type

是否必选

参数类型

参数说明

Y

Y

Y

Y

Y

Y

str

str

str

str

int

int

股票代码

K线周期

起始时间

结束时间

截取K线数量

复权类型

dividend_type的取值为：0不复权 1前复权 2后复权

count为截取最新交易日开始往前的n条K线，当count参数不为0时，start_time和end_time失效

count=-1时，获取所有数据，count=-2时，使用无序列数据

当count为0时，start_time和end_time生效，指定K线为对应时间段内

count最大值为24000，count为-1时为获取对应股票全部K线

设置的数据在断开连接前一直生效，后设置的数据会覆盖前面设置的数据

from tqcenter import tq

tq.initialize(__file__)

接口使用

1

2

3

4

5

6

数据样本

formula_set_res = tq.formula_set_data_info(stock_code='688318.SH',stock_period='1d', count=100,dividend_type=1)

print(formula_set_res)

1

{'ErrorId': '0', 'Msg': '向通达信公式系统设置数据信息成功！', 'run_id': '1'}

py

py

 通达信量化平台

← 向通达信公式设置数据formula_set_data

获取公式中的设置数据formula_get_data →

 通达信量化平台

获取公式中的设置数据formula_get_data

获取目前公式设置中的K线数据，使用前须先调用formula_set_data或formula_set_data_info设置公式数据

1

    def formula_get_data(cls):

py

py

接口使用

1

2

3

4

5

6

7

数据样本

1

2

3

4

5

6

from tqcenter import tq

tq.initialize(__file__)

formula_set_res = tq.formula_set_data_info(stock_code='688318.SH',stock_period='1d', count=5,dividend_type=1)

formula_kline = tq.formula_get_data()

print(formula_kline)

{'Code': '688318.SH', 'Data': [

{'Amount': 339302880.0, 'Close': 144.4, 'Date': '2026-01-20 00:00:00', 'High': 146.98, 'Low': 142.65, 'Open': 1

{'Amount': 358410880.0, 'Close': 144.77, 'Date': '2026-01-21 00:00:00', 'High': 146.5, 'Low': 143.1, 'Open': 14

{'Amount': 415987840.0, 'Close': 143.03, 'Date': '2026-01-22 00:00:00', 'High': 147.0, 'Low': 142.5, 'Open': 14

{'Amount': 471310432.0, 'Close': 144.39, 'Date': '2026-01-23 00:00:00', 'High': 146.88, 'Low': 142.58, 'Open':

{'Amount': 541417344.0, 'Close': 141.84, 'Date': '2026-01-26 00:00:00', 'High': 146.77, 'Low': 141.8, 'Open': 1

← 向通达信公式设置数据信息formula_set_data_info

调用通达信公式进行计算formula_zb/xg/exp →

py

py

 通达信量化平台

调用通达信公式进行计算formula_zb/xg/exp

调用通达信三种类型的公式

1

2

3

4

5

6

7

8

9

#调用技术指标公式

    def formula_zb(formula_name: str = '',

                   formula_arg: str = '',

                   xsflag: int = -1):

#调用条件选股公式

    def formula_xg(formula_name: str = '',

                   formula_arg: str = ''):

#调用专家系统公式

    def formula_exp(formula_name: str = '',

10

                    formula_arg: str = ''):

输入参数

参数

formula_name

formula_arg

xsflag

是否必选

参数类型

参数说明

Y

Y

Y

str

str

int

公式名称

公式参数

数据精度

目前支持调用技术指标公式、条件选股公式和专家系统公式，调用公式时请注意对应不同的调用接口和公式名

formula_arg格式为"arg1,arg2,arg3,arg4,arg5"，arg须为纯数字字符串，最多支持16个。

xsflag小于0时返回默认精度，最大可返回8位小数。

接口使用

1

2

3

4

5

6

7

8

9

10

11

12

13

14

数据样本

1

2

3

from tqcenter import tq

tq.initialize(__file__)

formula_set_res = tq.formula_set_data_info(stock_code='688318.SH',stock_period='1d', count=20,dividend_type=1)

#技术指标公式MACD

formula_zb = tq.formula_zb(formula_name='MACD', formula_arg='12,26,9')

print(formula_zb)

#条件选股公式UPN

formula_xg = tq.formula_xg(formula_name='UPN', formula_arg='3')

print(formula_xg)

#专家系统公式CCI

formula_exp = tq.formula_zb(formula_name='CCI', formula_arg='12')

print(formula_exp)

{'Data': {'DEA': [0.0, 0.01, -0.01, 0.03, 0.29, 0.63, 0.93, 1.25, 1.77, 2.27, 2.72, 3.08, 3.4, 3.57, 3.62, 3.58

{'Data': {'UP3': [None, None, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0

{'Data': {'ENTERLONG': [None, None, None, None, None, None, None, None, None, None, None, 0.0, 0.0, 0.0, 0.0, 0

 通达信量化平台

← 获取公式中的设置数据formula_get_data

批量调用通达信公式formula_process_mul_xg/zb →

 通达信量化平台

批量调用通达信公式formula_process_mul_xg/zb

批量调用通达信公式无需使用formula_set_data和formula_set_data_info提前设置，formula_set_data和formula_set_data_info
的设置也对批量调用不生效

py

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

#批量调用选股公式

def formula_process_mul_xg(formula_name: str = '',

                           formula_arg: str = '',

                           return_count: int = 1,

   return_date:bool = False,

   stock_list: List[str] = [],

   stock_period: str = '1d',

   start_time: str = '',

   end_time: str = '',

   count: int = 0,

   dividend_type: int = 0):

#批量调用指标公式

def formula_process_mul_zb(formula_name: str = '',

formula_arg: str = '',

xsflag: int = -1,

return_count: int = 1,

return_date:bool = False,

stock_list: List[str] = [],

stock_period: str = '1d',

start_time: str = '',

end_time: str = '',

count: int = 0,

dividend_type: int = 0):

输入参数

参数

formula_name

formula_arg

xsflag

retrun_count

formula_arg

stock_list

stock_period

start_time

end_time

count

dividend_type

是否必选

参数类型

参数说明

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

Y

str

str

int

int

公式名称

公式参数

数据精度

设置每个返回值的返回数

bool

设置是否返回日期

List[str]

股票代码列表

str

str

str

int

int

K线周期

起始时间

结束时间

截取K线数量

复权类型

dividend_type的取值为：0不复权 1前复权 2后复权

count为截取最新交易日开始往前的n条K线，当count参数不为0时，start_time和end_time失效

count=-1时，获取所有数据，count=-2时，使用无序列数据

 通达信量化平台

当count为0时，start_time和end_time生效，指定K线为对应时间段内

count最大值为24000，count为-1时为获取对应股票全部K线

正常每个返回值的数据个数应该与count相同，但是return_count可以限制返回个数，去掉用不到的数据，以此提高能够返回

py

的有效数据量

xsflag小于0时返回默认精度，最大可返回8位小数。

接口使用

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

from tqcenter import tq

tq.initialize(__file__)

#批量调用UPN 选股公式

mul_xg_res = tq.formula_process_mul_xg(

    formula_name='UPN',

    formula_arg='3',

    return_count=3,

    return_date=True,

    stock_list=['688318.SH','600519.SH','000001.SZ'],

    stock_period='1d',

    count=5,

    dividend_type=1)

print(mul_xg_res)

#批量调用CYX 指标公式

mul_zb_res = tq.formula_process_mul_zb(

    formula_name='CYX',

    formula_arg='12',

    return_count=3,

    return_date=True,

    stock_list=['688318.SH','600519.SH','000001.SZ'],

    stock_period='1d',

    count=5,

    dividend_type=1)

print(mul_zb_res)

数据样本

1

2

3

4

5

6

7

{'000001.SZ': {'UP3': [{'Date': '20260203', 'Value': '0'}, {'Date': '20260204', 'Value': '0'}, {'Date': '202602

'600519.SH': {'UP3': [{'Date': '20260203', 'Value': '0'}, {'Date': '20260204', 'Value': '1'}, {'Date': '2026020

'688318.SH': {'UP3': [{'Date': '20260203', 'Value': '0'}, {'Date': '20260204', 'Value': '0'}, {'Date': '2026020

{'000001.SZ': {'NOTEXT1': [{'Date': '20260203', 'Value': '11.06'}, {'Date': '20260204', 'Value': '11.08'}, {'Da

'600519.SH': {'NOTEXT1': [{'Date': '20260203', 'Value': '1494.05'}, {'Date': '20260204', 'Value': '1529.53'}, {

'688318.SH': {'NOTEXT1': [{'Date': '20260203', 'Value': '136.60'}, {'Date': '20260204', 'Value': '135.30'}, {'D

← 调用通达信公式进行计算formula_zb/xg/exp

常量枚举 →

 通达信量化平台

市场类型

名称

类型

数值

说明

.SZ

.SH

.BJ

.NQ

.SHO

.SZO

.HK

.US

.CSI

.CNI

.HG

.CFF

.CZC

.DCE

.SHF

.GFE

.INE

.HI

int

int

int

int

int

int

int

int

int

int

int

int

int

int

int

int

int

int

0

1

2

深圳交易所

上海交易所

北京交易所

44

新三板

8

9

31

74

62

上海个股期权

深圳个股期权

港股个股

美国股票

中证指数

102

国证指数

38

47

28

29

30

66

30

27

国内宏观指标

中金期货

郑州期货

大连期货

上海期货

广州期货

上海能源

港股指数

dividend_type复权类型

名称

类型

数值

说明

type

type

type

str

str

str

none

不复权

front

前复权

back

后复权

period周期入参类型

名称

类型

数值

说明

period

period

period

str

str

str

1m

5m

1分钟

5分钟

15m

15分钟

类型
 通达信量化平台

名称

数值

说明

period

period

period

period

period

period

period

period

str

str

str

str

str

str

str

str

30m

30分钟

1h

1d

1w

60分钟（1小时）

1天

1周

1mon

1月

1q

1y

1季

1年

tick

分笔

← 批量调用通达信公式formula_process_mul_xg/zb

回测及模拟交易 →

 通达信量化平台

什么是量化交易

量化交易是指利用计算机科技并采用一定的数学模型去实现投资理念、实现投资策略的过程。简单的说，量化交易主要是做这样

的事：

一个简单的投资想法 => 可执行的交易策略 => 可执行的代码程序 => 检验交易策略效果 => 实盘交易验证改进

Step 1：从一个简单的投资想法开始

投资想法即我们认为可能会盈利的投资方法、理念，比如熊市时期银行股是潜力股、复制基金经理的增强指数、金叉买入死叉卖

出等等。这些想法通常以网络、书本和讲座等为载体，来源于投顾、同行以及自己的经验总结等等。

以一个简单的投资想法为例：

1

2

如果遇到股价金叉，则买入

如果遇到股价死叉，则卖出

Step 2：完善这个想法，形成明确的可执行的交易策略

简单的投资想法通常比较模糊，我们需要将其细化成明确的可执行的策略，目的是为了能得到确定的信号进行交易操作。

一个可执行的交易策略至少需要明确以下几点:

1. Security：确定投资品种或范围

2. Condition：确定触发买/卖的具体条件

3. Quantity：确定买卖的数量/金额等

明确的可执行的交易策略的判断基准：根据交易策略的描述，不同的人在相同情形下，都能做出相同的交易操作。

上述关于金叉死叉的投资想法，显然它是不够明确的（可度量/可计算）。所以我们进一步细化：

1

2

3

监测沪深300指数的所有成分股的收盘价

如果收盘价上穿收盘价的5日简单移动平均，则用全部可用资金买入该股票

如果收盘价的5日简单移动平均上穿收盘价，则卖出该股票所有持仓

py

py

现在，我们基本已经把之前的想法细化成了明确的可执行的交易策略。当然，可能还有些地方不够明确或者参数需要改动，这些

可以随时想到随时修正，不必一次做到完美。

现在，我们想知道这样操作究竟会不会赚钱？

Step 3：编写一段代码，把交易策略转成可执行的代码程序

为了验证这个策略是否赚钱，我们需要把明确后的交易策略通过编程转成程序，计算机能根据历史数据/实时数据执行该策略产

生模拟交易，或者根据实时数据执行该策略产生实盘交易。

把上述策略翻译成计算机可以识别的代码语言，即类似这样的代码：

py

1

2

3

4

5

import pandas as pd

import vectorbt as vbt

from tqcenter import tq

6

tq.initialize(__file__)

 通达信量化平台

7

# 解决 pandas future warning

pd.set_option('future.no_silent_downcasting', True)

# ========================= 核心配置（用户可直接修改这里）=========================

target_start = '20240930'  # 【目标回测开始时间】（真正想回测的起始日）

target_end = '20250930'    # 【目标回测结束时间】

stock_code_list = ['688318.SH']     # 股票代码

window = 5         # MA指标周期（如MA5、MA10、MA20，改这里自动适配历史数据）

# ================================================================================

start_time = (pd.to_datetime(target_start) - pd.Timedelta(days=window + 10)).strftime('%Y%m%d')

# 1.获取价格数据

df_real = tq.get_market_data(

    field_list=['Close', 'Open'],

    stock_list=stock_code_list,

    start_time=start_time,

    end_time=target_end,

    dividend_type='front',

    period='1d',

    fill_data=True

)

close_df = tq.price_df(df_real, 'Close', column_names=stock_code_list)

open_df = tq.price_df(df_real, 'Open', column_names=stock_code_list)

# 2.买卖信号计算与生成

ma5_dynamic = vbt.MA.run(close_df, window=window).ma

ma5_dynamic.columns = close_df.columns

entries_raw = close_df.vbt.crossed_above(ma5_dynamic)

exits_raw = close_df.vbt.crossed_below(ma5_dynamic)

# 信号移位+1

entries_df = entries_raw.shift(1).fillna(False).astype(bool)

exits_df = exits_raw.shift(1).fillna(False).astype(bool)

# 3. 执行回测

portfolio = vbt.Portfolio.from_signals(

    close=close_df,             # 净值计算用未复权收盘价

    entries=entries_df,              # 延迟后的买入信号

    exits=exits_df,                  # 延迟后的卖出信号

    price=open_df,                # 含滑点的成交价格

    init_cash=100000,            #  初始资金10万元

    fees=0.0003,                  # 手续费0.03%（双边）

    freq='D',                     # 日线频率

    size_granularity=100          # A股最小交易单位100股

)

# 4. 输出回测结果

print(f"\n======投资组合回测表现=====")

print(portfolio.stats())

print(f"\n======投资组合回测记录======")

print(portfolio.trades.records_readable)

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

53

54

55

56

57

58

59

60

61

62

63

64

这样一来，刚才细化好的策略转成了代码，计算机就能理解并执行了。

 通达信量化平台

Step 4：回测或者模拟交易，检验策略效果

基本的检验策略方法有回测和模拟交易两种方法。核心区别是：回测是用历史数据模拟执行策略，模拟交易是用未来的实际数据

模拟执行策略。。

**回测是让计算机能根据一段时间区间内的历史的数据来模拟执行该策略，根据结果评价并改进策略。**如果结果不好，则需要

分析原因并改进。如果结果不错，则可以考虑用模拟交易进一步验证。

**模拟交易是让计算机能根据未来的实际数据模拟执行该策略一段时间区间，根据结果评价并改进策略。**如果策略在回测与模

拟交易的表现都非常好，我们可以考虑进行完全真金白银的实盘交易。

回测举例说明：

1. 策略环境：设定初始虚拟资产100万元；选择一段历史时间区间：20100101到20200101；把该时间区间的各种数据如收盘股

价行情等发给计算机。

2. 策略执行：计算机利用这些数据模仿历史真实的市场，执行我们编写的策略程序。

3. 策略评估：计算机会出具一份报告，根据这个报告我们知道，在20100101期初的100万元，按照我们的策略交易到期末

20200101，会怎样？一般包括盈亏情况，下单情况，持仓变化，以及一些统计指标等，根据此评估交易策略的好坏。

模拟交易举例说明：

1. 策略环境：设定初始的虚拟资产比如100万元，选择开始执行模拟交易的时间点，比如下周一。那么从下周一开始，股市开始

交易，真实的行情数据就会实时地发送到计算机。

2. 策略执行：计算机利用真实的数据模仿真实的市场，执行你的策略代码输出买卖队列，模拟系统会记录每一笔买卖记录。

3. 策略评估：我们可以得到一份实时更新的策略评估报告，这报告类似于回测得到的报告，不同的是会根据实际行情变化更新；

同样我们能据此评估交易策略的好坏。

Step 5：实盘执行交易策略，并持续优化改进策略

实盘交易就是让计算机能根据实际行情，用真实资金账号来自动下单交易。注意，这时不再是用虚拟资产进行模拟交易，实盘交

易账户上的盈亏都是真金白银。

实盘交易一般也会给出一份类似模拟交易的投资分析报告，通过实时观察策略的实盘表现、根据投资理念的变化、市场状况的变

化及时修正、改善和优化策略，使之保持持续盈利能力。

← 常量枚举

执行选股入板块 →

 通达信量化平台

执行选股策略并加入客户端自定义板块

第一步：执行选股策略

py

import pandas as pd

import numpy as np

from datetime import datetime

from tqcenter import tq

# 初始化tq

tq.initialize(__file__)

# 1. 基础配置（可修改项）

batch_codes = tq.get_stock_list_in_sector('通达信88')    # 目标板块

start_time = "20251025"                                  # 数据起始日期

target_end = datetime.now().strftime("%Y%m%d")           # 数据结束日期（当前日期）

N = 3                                                    # 目标连续上涨天数

block_code = 'LZXG'                                      # 自定义板块简称（必选）

block_name = '连涨选股'                                   # 自定义板块名称（必选）

# 2. 获取并整理收盘价数据

df_real = tq.get_market_data(

    field_list=['Close'],

    stock_list=batch_codes,

    start_time=start_time,

    end_time=target_end,

    dividend_type='front',  # 前复权

    period='1d',            # 日线

    fill_data=True          # 填充缺失数据

)

# 转换为「日期×股票代码」的收盘价宽表

close_df = tq.price_df(df_real, 'Close', column_names=batch_codes)

# 3. 标记每日是否上涨（核心判断逻辑）

is_up = close_df > close_df.shift(1)  # True=当日上涨，False=当日非上涨

# 4. 核心：计算连续上涨天数

# 步骤1：上涨日标记为1，非上涨日标记为NaN

up_mask = np.where(is_up, 1, np.nan)

up_mask_df = pd.DataFrame(up_mask, index=close_df.index, columns=close_df.columns)

# 步骤2：前向填充 → 连续上涨阶段的非上涨日（NaN）会被1填充

filled_df = up_mask_df.ffill()

# 步骤3：累计非NaN值的数量（初步计数）

consec_up_days = filled_df.notna().cumsum()

# 步骤4：非上涨日重置计数（关键步骤，实现“连续”效果）

reset_counts = consec_up_days.where(~is_up).ffill().fillna(0)

consec_up_days = (consec_up_days - reset_counts).astype(int)

# 5. 筛选符合条件的股票（连续上涨≥N天）

latest_date = consec_up_days.index[-1]  # 最新交易日

latest_consec_up = consec_up_days.loc[latest_date]  # 每只股票最新的连续上涨天数

target_stocks = latest_consec_up[latest_consec_up >= N].sort_values(ascending=False)

target_stocks_list = target_stocks.index.tolist()  # 提取符合条件的股票代码列表

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

53

54

# 6. 先创建自定义板块，再执行添加/清空操作

 通达信量化平台

55

print(f"\n=== 筛选结果（连续上涨≥{N}天）===")

56

57

58

59

60

61

62

63

64

65

66

67

68

69

70

71

72

73

74

75

76

77

78

79

80

81

82

83

84

85

86

87

88

89

90

91

92

93

94

95

96

97

98

99

# 第一步：创建自定义板块

try:

    tq.create_sector(block_code=block_code, block_name=block_name)
    print(f"✅ 已成功创建自定义板块「{block_name}（{block_code}）」")
except Exception as e:

    # 板块已存在时可能报错，此处捕获异常不中断流程
    print(f"ℹ  自定义板块创建提示：{e}（若提示已存在，可忽略此信息）")

# 第二步：处理板块成份股（添加/清空）

if not target_stocks.empty:

    # 打印筛选结果

    print(f"符合条件的股票共 {len(target_stocks)} 只：")

    for stock_code, days in target_stocks.items():

        print(f"{stock_code}：连续上涨 {days} 天")

    # 发送至自定义板块

    try:

        tq.send_user_block(block_code=block_code, stocks=target_stocks_list)
        print(f"\n✅ 已成功将股票添加至自定义板块「{block_name}（{block_code}）」")
    except Exception as e:
        print(f"\n❌ 添加自定义板块失败：{e}")

    # 发送提示消息至TQ策略管理器

    msg = f"MSG,筛选结果：{start_time}至{target_end}，连续上涨≥{N}天的股票共{len(target_stocks)}只，已添加至「{bloc

    try:

        tq.send_message(msg)
        print("✅ 提示消息发送成功")
    except Exception as e:
        print(f"❌ 消息发送失败：{e}")
else:

    # 无符合条件股票时清空板块

    print("暂无符合条件的股票")

    try:

        tq.send_user_block(block_code=block_code, stocks=[])
        print(f"✅ 已清空自定义板块「{block_name}（{block_code}）」")
    except Exception as e:
        print(f"❌ 清空自定义板块失败：{e}")

    # 发送空结果提示

    msg = f"MSG,筛选结果：{start_time}至{target_end}，连续上涨≥{N}天的股票共0只，已清空「{block_name}（{block_code}

    try:

        tq.send_message(msg)

    except Exception as e:
        print(f"❌ 消息发送失败：{e}")

第二步：客户端查看执行效果

 通达信量化平台

← 回测及模拟交易

订阅行情涨幅突破实时预警 →

 通达信量化平台

订阅行情涨幅突破实时预计

第一步：设置预警条件，并发送预警结果到客户端

#订阅板块成分股行情，涨幅突破实时预警，首次突破后取消该证券行情订阅监控

py

import json

import time

import signal

import sys

from datetime import datetime, timedelta

from collections import defaultdict

from tqcenter import tq

# ===================== 全局配置 =====================

# 板块配置：支持多个板块/自定义板块

SECTOR_NAMES = ['通达信88']  # 可扩展为其他板块名称或代码

PRICE_RISE_THRESHOLD = 5.0  # 涨幅阈值>5%

ANTI_SHAKE_SECONDS = 10      # 防抖间隔

BATCH_SUBSCRIBE_SIZE = 50    # 分批订阅大小（避免单次订阅过多）

# 全局变量

SUBSCRIBE_CODES = []         # 动态获取的监控股票列表

last_warn_time = defaultdict(int)

EXIT_FLAG = False

TRIGGERED_STOCKS = set()     # 记录已首次触发预警的股票（避免重复监控/推送）

# ===================== 信号处理函数 =====================

def signal_handler(signum, frame):

    """处理Ctrl+C（SIGINT）信号"""

    global EXIT_FLAG

    print(f"\n\n[{datetime.now().strftime('%H:%M:%S')}] 接收到退出信号（Ctrl+C），开始清理资源...")

    EXIT_FLAG = True

    # 强制取消订阅+关闭TDX

    try:

        unsubscribe_stocks()

    except Exception as e:

        print(f"取消订阅失败：{e}")

    print("资源清理完成，程序退出！")

    sys.exit(0)

# ===================== 工具函数（新增） =====================

def get_valid_stock_codes(sector_names):

    """

    从指定板块获取有效股票代码列表

    :param sector_names: 板块名称列表

    :return: 去重后的有效股票代码列表

    """

    valid_codes = set()  # 用集合去重

    for sector in sector_names:

        try:

            # 获取板块股票列表（TDX初始化后调用）

            sector_codes = tq.get_stock_list_in_sector(sector)

            if not sector_codes:

                print(f"[{datetime.now().strftime('%H:%M:%S')}] 警告：板块{sector}未获取到股票列表")

                continue

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

53

54

            # 过滤无效代码（空值、格式错误）

 通达信量化平台

55

            for code in sector_codes:

56

57

58

59

60

61

62

63

64

65

66

67

68

69

70

71

72

73

74

75

76

77

78

79

80

81

82

83

84

85

86

87

88

89

90

91

92

93

94

95

96

97

98

99

100

101

102

103

104

105

106

107

108

109

110

111

112

113

114

115

                if code and isinstance(code, str) and (code.endswith('.SH') or code.endswith('.SZ')):

                    valid_codes.add(code)

                else:

                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 过滤无效代码：{code}")

        except Exception as e:

            print(f"[{datetime.now().strftime('%H:%M:%S')}] 获取板块{sector}股票列表失败：{e}")

            import traceback

            traceback.print_exc()

    # 转为列表并排序

    valid_codes_list = sorted(list(valid_codes))

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 从板块{sector_names}获取到有效股票{len(valid_codes_list)}只：

    return valid_codes_list

def batch_subscribe(stocks, batch_size):

    """

    分批订阅股票（避免单次订阅过多）

    :param stocks: 股票列表

    :param batch_size: 每批订阅数量

    :return: 整体订阅结果（True/False）

    """

    total_success = True

    for i in range(0, len(stocks), batch_size):

        batch = stocks[i:i+batch_size]

        try:

            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 订阅第{i//batch_size + 1}批股票（{len(batch)}只）：

            sub_res = tq.subscribe_hq(stock_list=batch, callback=price_rise_callback)

            if not sub_res:

                print(f"[{datetime.now().strftime('%H:%M:%S')}] 第{i//batch_size + 1}批订阅失败：{sub_res}")

                total_success = False

            else:

                print(f"[{datetime.now().strftime('%H:%M:%S')}] 第{i//batch_size + 1}批订阅成功：{sub_res}")

        except Exception as e:

            print(f"[{datetime.now().strftime('%H:%M:%S')}] 第{i//batch_size + 1}批订阅异常：{e}")

            total_success = False

    return total_success

def unsubscribe_single_stock(stock_code):

    """

    取消单只股票的订阅（首次触发后不再监控）

    :param stock_code: 股票代码

    :return: 取消结果（True/False）

    """

    try:

        un_sub_res = tq.unsubscribe_hq(stock_list=[stock_code])

        if un_sub_res:

            # 从全局订阅列表中移除

            if stock_code in SUBSCRIBE_CODES:

                SUBSCRIBE_CODES.remove(stock_code)

            return True

        return False

    except Exception as e:

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 取消{stock_code}订阅失败：{e}")

        return False

# ===================== 核心回调函数 =====================

def price_rise_callback(data_str):

    try:

        code_json = json.loads(data_str)

116

        code = code_json.get('Code')

 通达信量化平台

117

118

119

120

121

122

123

124

125

126

127

128

129

130

131

132

133

134

135

136

137

138

139

140

141

142

143

144

145

146

147

148

149

150

151

152

153

154

155

156

157

158

159

160

161

162

163

164

165

166

167

168

169

170

171

172

173

174

175

176

177

        # 前置过滤：无效数据/非监控股票/已触发过的股票（直接返回，不输出日志）

        if (code_json.get('ErrorId') != "0" or not code) or \

           (code not in SUBSCRIBE_CODES) or \

           (code in TRIGGERED_STOCKS):

            return

        # 获取最新行情数据

        report_ptr = tq.get_full_tick(code)

        latest_price = 0.0

        pre_close = 0.0

        if report_ptr:

            latest_price = round(float(report_ptr['Now']), 2)

            pre_close = round(float(report_ptr['LastClose']), 2)

            if pre_close <= 0 and latest_price > 0:

                pre_close = latest_price - 0.01

        # 过滤最新价/昨收价无效的情况

        if latest_price <= 0 or pre_close <= 0:

            return

        # 计算涨幅

        rise_rate = round(((latest_price - pre_close) / pre_close) * 100, 2) if pre_close > 0 else 0.0

        # 仅处理满足涨幅阈值+防抖的情况

        if rise_rate > PRICE_RISE_THRESHOLD:

            current_time = int(time.time())

            if current_time - last_warn_time[code] < ANTI_SHAKE_SECONDS:

                return

            # 标记为已触发，后续不再处理

            TRIGGERED_STOCKS.add(code)

            last_warn_time[code] = current_time

            # 取消该股票的订阅（不再监控）

            unsubscribe_single_stock(code)

            # 发送预警

            warn_time = datetime.now().strftime("%Y%m%d%H%M%S")

            reason = (

                f"涨幅突破"

            )

            try:

                # 成交量用实际值，无则填0

                volume = report_ptr.get('Volume', '0') if report_ptr else '0'

                warn_res = tq.send_warn(

                    stock_list=[code],

                    time_list=[warn_time],

                    price_list=[str(latest_price)],

                    close_list=[str(pre_close)],

                    volum_list=[volume],

                    bs_flag_list=['0'],

                    warn_type_list=['3'],

                    reason_list=[reason],

                    count=1

                )

                print(f"[{datetime.now().strftime('%H:%M:%S')}] {reason}")

178

                print(f"[{datetime.now().strftime('%H:%M:%S')}] 预警发送结果：{warn_res}")

 通达信量化平台

179

                print(f"[{datetime.now().strftime('%H:%M:%S')}] 已取消{code}订阅，后续不再监控")

180

181

182

183

184

185

186

187

188

189

190

191

192

193

194

195

196

197

198

199

200

201

202

203

204

205

206

207

208

209

210

211

212

213

214

215

216

217

218

219

220

221

222

223

224

225

226

227

228

229

230

231

232

233

234

235

236

237

238

239

            except Exception as e:

                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {code} 发送预警失败：{e}")

    except Exception as e:

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 回调函数执行异常：{e}")

        import traceback

        traceback.print_exc()

    return None

# ===================== 订阅/取消订阅函数=====================

def subscribe_stocks():

    """订阅股票（分批订阅+容错）"""

    if not SUBSCRIBE_CODES:

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 无有效股票可订阅，跳过订阅流程")

        return False

    print(f"\n开始批量订阅股票（总计{len(SUBSCRIBE_CODES)}只）")

    sub_result = batch_subscribe(SUBSCRIBE_CODES, BATCH_SUBSCRIBE_SIZE)

    print(f"批量订阅最终结果：{'成功' if sub_result else '部分/全部失败'}")

    return sub_result

def unsubscribe_stocks():

    """取消订阅（分批取消）"""

    if not SUBSCRIBE_CODES:

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 无已订阅股票，跳过取消订阅流程")

        return False

    print(f"\n开始批量取消订阅股票（总计{len(SUBSCRIBE_CODES)}只）")

    total_success = True

    for i in range(0, len(SUBSCRIBE_CODES), BATCH_SUBSCRIBE_SIZE):

        batch = SUBSCRIBE_CODES[i:i+BATCH_SUBSCRIBE_SIZE]

        try:

            print(f"取消第{i//BATCH_SUBSCRIBE_SIZE + 1}批订阅：{batch[:5]}...")

            un_sub_ptr = tq.unsubscribe_hq(stock_list=batch)

            if not un_sub_ptr:

                print(f"第{i//BATCH_SUBSCRIBE_SIZE + 1}批取消失败：{un_sub_ptr}")

                total_success = False

        except Exception as e:

            print(f"第{i//BATCH_SUBSCRIBE_SIZE + 1}批取消异常：{e}")

            total_success = False

    print(f"批量取消订阅最终结果：{'成功' if total_success else '部分/全部失败'}")

    return total_success

# ===================== 主程序 =====================

if __name__ == "__main__":

    # 注册SIGINT信号处理（优先于默认的KeyboardInterrupt）

    signal.signal(signal.SIGINT, signal_handler)

    # 1. 初始化TDX（仅执行1次，无重试）

    try:

        tq.initialize(__file__)

        print(f"程序启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print(f"TDX初始化成功")

    except Exception as e:

        print(f"TDX初始化失败：{e}")

        exit(1)

    # 2. 获取板块股票列表

    SUBSCRIBE_CODES = get_valid_stock_codes(SECTOR_NAMES)

240

    if not SUBSCRIBE_CODES:

 通达信量化平台

241

        print("未获取到任何有效股票代码，程序退出")

        exit(1)

    # 3. 订阅股票

    subscribe_stocks()

    # 4. 运行提示

    print(f"\n=== 涨幅监控启动 ===")

    print(f"监控板块：{SECTOR_NAMES}")

    print(f"监控股票总数：{len(SUBSCRIBE_CODES)}")

    print(f"涨幅阈值：>{PRICE_RISE_THRESHOLD}%")

    print(f"防抖间隔：{ANTI_SHAKE_SECONDS}秒")

    print(f"分批订阅大小：{BATCH_SUBSCRIBE_SIZE}只/批")

    print("按 Ctrl+C 退出程序...\n")

    # 5. 通过全局标记控制退出

    try:

        while not EXIT_FLAG:

            time.sleep(0.1)

    except Exception as e:

        print(f"主循环异常：{e}")

        # 兜底清理

        unsubscribe_stocks()

242

243

244

245

246

247

248

249

250

251

252

253

254

255

256

257

258

259

260

261

262

263

264

第二步：打开通达信金融终端查看运行结果

通达信金融终端

← 执行选股入板块

计算调仓信号并快速买卖 →

py

 通达信量化平台

计算调仓信号并快速买卖

第一步：计算信号并发送预警，以

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

53

from datetime import datetime, timedelta

from tqcenter import tq as tdxdata

import vectorbt as vbt

import pandas as pd

# 初始化

tdxdata.initialize(__file__)

run_time = datetime.now()

run_time_str = run_time.strftime("%Y-%m-%d %H:%M:%S")

# 预警时间戳（格式：YYYYMMDDHHMMSS）

warn_time = run_time.strftime("%Y%m%d%H%M%S")

# ===================== 1. 配置参数 =====================

N = 5  # 均线周期

batch_codes = tdxdata.get_stock_list_in_sector('通达信88')

end_date = run_time.strftime("%Y%m%d")

start_date = (run_time - timedelta(days=2 * N + 20)).strftime("%Y%m%d")

# ===================== 2. 获取并处理数据 =====================

# 获取日线Close数据（保留完整索引用于日期筛选）

df_real = tdxdata.get_market_data(

    field_list=['Close'],

    stock_list=batch_codes,

    start_time=start_date,

    end_time=end_date,

    dividend_type='front',

    period='1d',

    fill_data=True

)

close_df = tdxdata.price_df(df_real, 'Close', column_names=batch_codes)

# 计算均线+生成信号

ma = vbt.MA.run(close_df, window=N).ma

ma.columns = close_df.columns

entries = close_df.vbt.crossed_above(ma)  # 上穿（买入）

exits = close_df.vbt.crossed_below(ma)    # 下穿（卖出）

latest_date = close_df.index[-1]  # 今日日期（DataFrame最后一行）

# 获取上一个工作日日期

prev_date = close_df.index[-2] if len(close_df.index) >= 2 else latest_date

# ===================== 3. 筛选最新买卖信号 =====================

buy_signals = {}

sell_signals = {}

# 遍历股票筛选信号

for code in batch_codes:

    # 确保股票有足够的交易数据

    if code not in close_df.columns:

        continue

    # 今日收盘价

    today_close = close_df.loc[latest_date, code]

    # 上一个工作日收盘价

54

    prev_close = close_df.loc[prev_date, code] if len(close_df.index) >= 2 else today_close

 通达信量化平台

55

56

57

58

59

60

61

62

63

64

65

66

67

68

69

70

71

72

73

74

75

76

77

78

79

80

81

82

83

84

85

86

87

88

89

90

91

92

93

94

95

96

97

98

99

100

101

102

103

104

105

106

107

108

109

110

111

112

113

114

115

    # 买入信号：最新日期Close上穿均线

    if entries.loc[latest_date, code]:

        buy_signals[code] = {

            'today_close': round(today_close, 2),    # 今日close

            'prev_close': round(prev_close, 2),      # 上一个工作日close

            'ma_price': round(ma.loc[latest_date, code], 2)

        }

    # 卖出信号：最新日期Close下穿均线

    if exits.loc[latest_date, code]:

        sell_signals[code] = {

            'today_close': round(today_close, 2),    # 今日close

            'prev_close': round(prev_close, 2),      # 上一个工作日close

            'ma_price': round(ma.loc[latest_date, code], 2)

        }

# ===================== 4. 生成并发送MSG =====================

def send_msg(content):

    msg = f"MSG,{content}"

    print(msg)

    try:

        tdxdata.send_message(msg)

    except Exception as e:

        print(f"发送失败: {e}")

# 统计行

stat_line = (

    f"运行时间：{run_time_str}，均线周期：{N}天，"

    f"买入信号数：{len(buy_signals)} 只，卖出信号数：{len(sell_signals)} 只"

)

print("\n=== MSG格式（TQ策略管理器显示区域）===")

send_msg(stat_line)

# 处理买入信号

if buy_signals:

    send_msg(f"=== 买入信号（Close上穿{N}日均线）===")

    for idx, (code, info) in enumerate(buy_signals.items(), 1):

        line = f"{idx}. {code}：买入信号，今日Close:{info['today_close']}，昨日Close:{info['prev_close']}"

        send_msg(line)

# 处理卖出信号

if sell_signals:

    send_msg(f"=== 卖出信号（Close下穿{N}日均线）===")

    for idx, (code, info) in enumerate(sell_signals.items(), 1):

        line = f"{idx}. {code}：卖出信号，今日Close:{info['today_close']}，昨日Close:{info['prev_close']}"

        send_msg(line)

# 无信号的情况

if not buy_signals and not sell_signals:

    send_msg(f"运行时间：{run_time_str}，均线周期：{N}天，无买入或卖出信号")

# ===================== 5. 调用send_warn接口发送预警 =====================

def send_trade_warn():

    """发送买卖信号对应的预警（精简版，仅保留核心逻辑）"""

    # 合并所有信号用于发送预警

    all_signals = []

    if buy_signals:

        all_signals.extend([(code, info, '买入') for code, info in buy_signals.items()])

    if sell_signals:

        all_signals.extend([(code, info, '卖出') for code, info in sell_signals.items()])

116

 通达信量化平台

117

    if not all_signals:

        print("\n无预警信息需要发送")

        return

    # 构造预警参数列表

    codes = []

    time_list = []

    price_list = []       # 今日close

    close_list = []       # 上一个工作日close

    volum_list = []

    bs_flag_list = []

    warn_type_list = []

    reason_list = []

    for code, info, trade_type in all_signals:

        codes.append(code)

        time_list.append(warn_time)

        price_list.append(str(info['today_close']))    # 替换为今日close

        close_list.append(str(info['prev_close']))     # 替换为上一个工作日close

        volum_list.append('0')

        bs_flag_list.append('0' if trade_type == '买入' else '1')

        warn_type_list.append('1')

        reason_list.append(f"{trade_type}信号")

    # 调用预警接口

    try:

        warn_res = tdxdata.send_warn(

            stock_list=codes,

            time_list=time_list,

            price_list=price_list,

            close_list=close_list,

            volum_list=volum_list,

            bs_flag_list=bs_flag_list,

            warn_type_list=warn_type_list,

            reason_list=reason_list,

            count=len(codes)

        )

        print(f"\n预警发送完成，共发送 {len(codes)} 条预警，接口返回：{warn_res}")

    except Exception as e:

        print(f"\n预警发送失败：{e}")

# 执行预警发送

send_trade_warn()

print("\n所有消息发送完成！")

tdxdata.close()

118

119

120

121

122

123

124

125

126

127

128

129

130

131

132

133

134

135

136

137

138

139

140

141

142

143

144

145

146

147

148

149

150

151

152

153

154

155

156

157

158

159

160

161

162

163

第二步:双击TQ策略信号，快速打开闪电买卖，根据输出的买/卖信号打开买/卖界面

注意：须保证交易账号已登录。

 通达信量化平台

← 订阅行情涨幅突破实时预警

结合VBT回测示例 →

 通达信量化平台

VBT简单回测并输出图形

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

53

54

55

56

# 注意：

# 1/目前调用的vectorbt三方库函数vbt.Portfolio.from_signals不支持分红送股等权益变动，该demo仅做示例。

py

import pandas as pd

import vectorbt as vbt    #VSCODE-终端安装1. pip install vectorbt -i https://pypi.tuna.tsinghua.edu.cn/simple

from tqcenter import tq

from datetime import datetime

tq.initialize(__file__)

# 解决 pandas future warning

pd.set_option('future.no_silent_downcasting', True)

pd.set_option('display.float_format', lambda x: f"{x:.10f}".rstrip('0').rstrip('.') if '.' in f"{x:.10f}" else

# ========================= 核心配置（用户可直接修改这里）=========================

target_start = '20250701'  # 【目标回测开始时间】（真正想回测的起始日）

target_end = '20251231'    # 【目标回测结束时间】

stock_code_list = ['688318.SH']     # 股票代码

window = 5         # MA指标周期（如MA5、MA10、MA20，改这里自动适配历史数据）

# ==========================================================

start_time = (pd.to_datetime(target_start) - pd.Timedelta(days=window + 10)).strftime('%Y%m%d')

# 1.获取价格数据

df_real = tq.get_market_data(

    field_list=['Close', 'Open'],

    stock_list=stock_code_list,

    start_time=start_time,

    end_time=target_end,

    dividend_type='front',

    period='1d',

    fill_data=True

)

close_df = tq.price_df(df_real, 'Close', column_names=stock_code_list)

open_df = tq.price_df(df_real, 'Open', column_names=stock_code_list)

# 2.买卖信号计算与生成

ma5_dynamic = vbt.MA.run(close_df, window=window).ma.ffill()

ma5_dynamic.columns = close_df.columns

entries_df = close_df.vbt.crossed_above(ma5_dynamic).shift(1).fillna(False).astype(bool)

exits_df = close_df.vbt.crossed_below(ma5_dynamic).shift(1).fillna(False).astype(bool)

print(f"\n信号生成统计:")

print(f"买入信号总数: {entries_df.sum().sum()}")

print(f"卖出信号总数: {exits_df.sum().sum()}")

# 3. 执行回测

portfolio = vbt.Portfolio.from_signals(

    close=close_df,             # 净值计算用未复权收盘价

    entries=entries_df,         # 延迟后的买入信号

    exits=exits_df,             # 延迟后的卖出信号

    price=open_df,              # 含滑点的成交价格

    init_cash=100000,           # 初始资金10万元

    fees=0.0003,                # 手续费0.03%（双边）

    freq='D',                   # 日线频率

57

    size_granularity=100        # A股最小交易单位100股

 通达信量化平台

58

)

59

60

61

62

63

64

65

66

67

68

69

70

71

72

73

74

# ========== vbt绘图 ==========

portfolio[stock_code_list[0]].plot().show()

# 4. 输出回测结果

print(f"\n" + "="*60)

print(f"投资组合回测表现")

print("="*60)

stats_df = portfolio.stats()

print(stats_df)

print(f"\n" + "="*60)

print(f"投资组合回测记录")

print("="*60)

trades_df_original = portfolio.trades.records_readable.copy()

print(trades_df_original.to_string())

← 计算调仓信号并快速买卖

公众号文章例子 →

 通达信量化平台

Q：运行的python文件可不可以随便放，不一定在PYPlugins\user目录下？

A： 可以。在import tqcenter前添加通达信安装目录\PYPlugins\user这个绝对路径。

1

2

3

4

import sys

sys.path.append('C:/new_tdx64/PYPlugins/user')

from tqcenter import tq

tq.initialize(__file__)

py

Q：无法内部执行策略之如何把python路径添加到PATH中

A： 内部执行python策略时，会寻找用户设定的默认python解释器执行python策略，所以必须在操作系统<高级系统设置>--->

环境变量设置里，配置python路径。

如图所示，环境变量中分为用户变量和系统变量，都有PATH，在这两个中添加python路径都可生效，但是用户变量的优先级高

于系统变量，所以图中仅在用户变量中的PATH中添加python路径。

 通达信量化平台

图中可见，PATH中可以配置多个版本的python，但是最后生效为最上面的，每个版本的python需要配置两个路径。

Q：出现类似以下的报错怎么办？

1

FileNotFoundError: Could not find module 'F:\tdx\new_tdx_600\PYPlugins\TPythClient.dll' (or one of its dependen

py

A： 这通常是TPythClient.dll缺少依赖库导致的，请检查TPythClient.dll同目录下（../PYPlugins/）是否有tdxrpcx64.dll，通常是杀

毒软件误杀此dll导致，需要重装或给予白名单确保tdxrpcx64.dll不会被杀毒软件误杀。

Q：获取的数据count=5，返回的指标值怎么前面的是none？

A： formula_set_res = tq.formula_set_data_info(stock_code=stock,stock_period='1d', count=4,dividend_type=1)这里的count=4

是获取最近4根k线的数据用于计算指标，所以最近4根k的数据

ZF:(C-REF(C,1))/REF(C,1)*100;这个式子的只能计算出 最后4根k的涨幅值。

所以在获取指标值时注意获取k线数目要覆盖到最大参数值，否则计算结果会为空。

Q：外部运行的py文件报已经存在运行的，怎么处理？

A： 请在TQ策略管理器找到这个正在运行的已经运行出错的OutSide策略，点删除策略删除它。

← 公众号文章例子

