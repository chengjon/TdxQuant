import json
import ctypes
import numpy as np
import pandas as pd
import weakref
import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Union
from collections import defaultdict
from datetime import datetime, timedelta
import re
import atexit
import inspect


dll_path = Path(__file__).resolve().parents[1] / 'TPythClient.dll'
dll = ctypes.CDLL(str(dll_path))

# 设置DLL函数的返回类型
dll.InitConnect.restype = ctypes.c_char_p       # 初始化 获取id
dll.GetStockListInStr.restype = ctypes.c_char_p  # 获取股票列表
dll.GetHISDATsInStr.restype = ctypes.c_char_p   # K线数据
dll.GetCWDATAInStr.restype = ctypes.c_char_p    # 复权数据
dll.Register_DataTransferFunc.restype=None      # 注册外套回调函数
dll.SubscribeGPData.restype=ctypes.c_char_p     # 订阅单股数据
dll.SubscribeHQDUpdate.restype=ctypes.c_char_p     # 订阅单股行情更新
dll.SetNewOrder.restype=ctypes.c_char_p         # 下单接口 
dll.GetSTOCKInStr.restype=ctypes.c_char_p       # 获取股票详细信息
dll.GetREPORTInStr.restype=ctypes.c_char_p      # 获取行情数据
dll.SetResToMain.restype=ctypes.c_char_p        # 获取行情数据
dll.GetBlockListInStr.restype=ctypes.c_char_p           # 获取板块列表
dll.GetBlockStocksInStr.restype=ctypes.c_char_p         # 获取板块成分股
dll.GetTradeCalendarInStr.restype=ctypes.c_char_p    # 获取交易日历数据
dll.ReFreshCacheAll.restype=ctypes.c_char_p    # 刷新缓存行情
dll.ReFreshCacheKLine.restype=ctypes.c_char_p    # 刷新缓存数据
dll.DownLoadFiles.restype=ctypes.c_char_p    # 下载文件
dll.UserBlockControl.restype=ctypes.c_char_p    # 自定义板块操作
dll.GetProDataInStr.restype=ctypes.c_char_p         # 获取专业数据
dll.GetCBINFOInStr.restype=ctypes.c_char_p         # 可转债基础信息
dll.GetIPOINFOInStr.restype=ctypes.c_char_p         # 新股申购信息

def _convert_time_format(start_time):
    """
    将起始时间转换为标准格式

    Args:
        start_time (str): 起始时间，格式为 YYYYMMDD 或 YYYYMMDDHHMMSS

    Returns:
        str: 格式化后的时间，格式为 YYYY-MM-DD HH:MM:SS

    Raises:
        ValueError: 当输入格式不正确时
    """
    # 根据输入长度判断时间格式
    if len(start_time) == 8:  # YYYYMMDD
        dt = datetime.strptime(start_time, '%Y%m%d')
    elif len(start_time) == 14:  # YYYYMMDDHHMMSS
        dt = datetime.strptime(start_time, '%Y%m%d%H%M%S')
    else:
        tq.close()
        raise ValueError("时间格式不正确，应为 YYYYMMDD 或 YYYYMMDDHHMMSS")

    # 转换为目标格式
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def dynamic_qmt_converter(financial_data):
    """
    动态转换财务数据为QMT格式，自动识别所有报表类型
    """
    result = {}
    
    # 动态识别所有报表类型（排除ErrorId等非报表字段）
    statement_types = []
    for key, value in financial_data.items():
        if (key != 'ErrorId' and 
            isinstance(value, dict) and 
            'm_timetag' in value):
            statement_types.append(key)
    
    #print(f"自动识别的报表类型: {statement_types}")
    
    for statement_type in statement_types:
        statement_data = financial_data[statement_type]
        
        # 获取时间标签
        time_tags = statement_data['m_timetag']
        
        df_data = {}
        # 处理所有非元数据字段
        for key, values in statement_data.items():
            # 跳过时间相关元数据字段
            if key.startswith('m_'):
                continue
                
            # 检查数据有效性
            if (isinstance(values, list) and 
                len(values) == len(time_tags)):
                
                # 尝试转换为数值类型
                try:
                    numeric_values = []
                    for v in values:
                        try:
                            # 尝试转换为float，失败则保持原样
                            numeric_value = float(v) if v != '' and v is not None else v
                            numeric_values.append(numeric_value)
                        except (ValueError, TypeError):
                            numeric_values.append(v)
                    df_data[key] = numeric_values
                except Exception as e:
                    print(f"转换字段 {statement_type}.{key} 时出错: {e}")
                    df_data[key] = values
        
        # 创建DataFrame
        if df_data:
            try:
                df = pd.DataFrame(df_data, index=time_tags)
                df.index.name = 'time'
                
                # 添加公告时间作为列（如果需要）
                if 'm_anntime' in statement_data:
                    df['announce_time'] = statement_data['m_anntime']
                
                result[statement_type] = df
                #print(f"成功创建 {statement_type} 表格，包含 {len(df.columns)} 个指标")
                
            except Exception as e:
                print(f"创建 {statement_type} DataFrame 时出错: {e}")
        else:
            print(f"警告: {statement_type} 没有可用的指标数据")
    
    return result


def merge_all_statements(converted_data):
    """
    合并所有报表到一个DataFrame
    """
    all_dfs = []
    
    for stype, df in converted_data.items():
        # 为每个报表的列添加前缀以区分
        df_prefixed = df.copy()
        df_prefixed.columns = [f"{stype}_{col}" for col in df.columns]
        all_dfs.append(df_prefixed)
    
    if all_dfs:
        # 按时间索引合并所有DataFrame
        merged_df = pd.concat(all_dfs, axis=1, join='outer')
        return merged_df
    else:
        return pd.DataFrame()

def convert_or_validate(data):
    """
    如果输入是list，则根据后缀(SZ=0, SH=1, BJ=2)转换为“0#600000|1#600001|2#600002”格式的字符串
    如果输入是字符串，则验证是否符合指定格式
    
    Args:
        data: list或str类型的数据
        
    Returns:
        str: 转换后的字符串或验证结果
    """
    # 定义后缀到编号的映射
    suffix_map = {
        'SZ': '0',
        'SH': '1', 
        'BJ': '2',
        '0': '0',
        '1': '1',
        '2': '2'
    }
    
    if isinstance(data, list):
        # 处理列表转换
        result = []
        for item in data:
            # 分割代码和后缀
            if '.' not in item:
                print(f"无效的格式: {item}，需要包含后缀(.SZ/.SH/.BJ)")
                return ""
            
            code, suffix = item.split('.', 1)
            
            if suffix not in suffix_map:
                print(f"不支持的后缀: {suffix}, 只支持SZ/SH/BJ")
                return ""
            
            # 根据后缀获取对应的编号
            num = suffix_map[suffix]
            result.append(f"{num}#{code}")
        
        return "|".join(result)
    
    elif isinstance(data, str):
        # 验证字符串格式
        parts = data.split("|")
        
        # 检查是否包含所有必要的部分
        if len(parts) < 1:
            return ""
        
        # 检查每个部分的格式
        for part in parts:
            if '#' not in part:
                return ""
            
            num, code = part.split('#', 1)
            
            # 检查编号是否有效
            if num not in ['0', '1', '2']:
                return ""
            
            # 检查代码是否为6位数字
            if not code.isdigit() or len(code) != 6:
                return ""
        
        return data
    
    else:
        # 不支持的类型
        print("输入必须是list或str类型")
        return ""
    
def get_python_version_number() -> int:
    """
    获取当前Python版本号，提取主、次版本拼接为数字（如3.13.7返回313）
    
    Returns:
        int: 主+次版本拼接的数字
    """
    version_info = sys.version_info
    major = version_info.major  # 主版本（如3）
    minor = version_info.minor  # 次版本（如13）
    version_num = major * 100 + minor  # 拼接为数字（3*100+13=313）
    
    return version_num

def get_warn_struct_str(stock_list:        List[str] = [],
                  time_list:         List[str] = [],
                  price_list:        List[str] = [],
                  close_list:        List[str] = [],
                  volum_list:        List[str] = [],
                  bs_flag_list:      List[str] = [],
                  warn_type_list:    List[str] = [],
                  reason_list:       List[str] = [],
                  count:        int  = 1) -> str:
    """
    获取预警结构字符串
    """
    # 1. 校验stock_list格式
    stock_pattern = re.compile(r'^\d{6}\.[A-Z]+$')
    for stock in stock_list:
        if not stock_pattern.match(stock):
            tq.close()
            raise ValueError(f"股票代码格式错误: {stock}（需6位数字+市场后缀，如688318.SH）")

    # 2. 校验必须满足count长度的列表
    required_lists = {
        "stock_list": stock_list,
        "price_list": price_list,
        "close_list": close_list,
        "volum_list": volum_list
    }
    for name, lst in required_lists.items():
        if len(lst) < count:
            tq.close()
            raise ValueError(f"{name}元素数量不足（当前{len(lst)}，需要{count}）")
        
    time_list = [_convert_time_format(time_str) for time_str in time_list]
    # 3. 补全其他列表
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 补全warn_time（缺则补当前时间）
    filled_warn_time = time_list[:count] + [current_time] * max(0, count - len(time_list))
    # 补全bs_flag（缺则补2）
    filled_bs_flag = bs_flag_list[:count] + ["2"] * max(0, count - len(bs_flag_list))
    # 补全warn_type（缺则补-1）
    filled_warn_type = warn_type_list[:count] + ["-1"] * max(0, count - len(warn_type_list))
    # 补全reason（缺则补空字符串）
    filled_reason = reason_list[:count] + [""] * max(0, count - len(reason_list))

    # 4. 截取每个列表的前count个元素
    parts = [
        ",".join(stock_list[:count]),
        ",".join(filled_warn_time),
        ",".join(price_list[:count]),
        ",".join(close_list[:count]),
        ",".join(volum_list[:count]),
        ",".join(filled_bs_flag),
        ",".join(filled_warn_type),
        ",".join(filled_reason)
    ]

    # 5. 拼接结果（不同元素用||分隔）
    return "|".join(parts)
        
def get_bt_struct_str(time_list:         List[str] = [],
                      data_list:       List[List[str]] = [],
                      count:        int  = 1) -> str:
    """
    获取回测结构字符串
    """
    # 1. 校验time_list长度
    if len(time_list) < count:
        raise ValueError(f"time_list长度不足（当前{len(time_list)}，需至少{count}）")

    time_list = [_convert_time_format(time_str) for time_str in time_list]
    # 2. 处理data_list：补全、截取、格式校验
    filled_data = data_list[:count] + ['0'] * max(0, count - len(data_list))  # 不足补0
    num_pattern = re.compile(r'^[0-9.]+$')  # 匹配纯数字（含整数/浮点数）
    processed_data = []
    
    for item in filled_data:
        truncated = item[:16]  # 取前16位
        for item2 in truncated:
            if not num_pattern.match(item2):
                raise ValueError(f"data_list元素非法：{truncated}（需为纯数字字符串）")
        processed_data.append(",".join(truncated))  # 重新拼接（保证格式统一）

    # 3. 按新格式拼接最终字符串
    time_part = ",".join(time_list[:count])  # time_list元素用","拼接
    data_part = ",,".join(processed_data)   # data_list元素整体用",,"拼接
    final_str = f"{time_part}|{data_part}"  # 最终time和data用||分隔

    return final_str

def check_stock_code_format(input_data):
    """
    校验输入的字符串/字符串列表是否符合「6位数字+市场后缀」的标准格式
    :param input_data: str | list[str]，待校验的单个股票代码或代码列表
    """
    if not input_data:
        print("入参不能为空")
        return False

    # 正则表达式：6位数字 + . + 2-3位大写字母（匹配.SH/.SZ/.JJ等）
    pattern = re.compile(r'^\d{6}\.[A-Z]{2,3}$')
    
    # 统一转为列表处理（兼容单个字符串/列表入参）
    if isinstance(input_data, str):
        check_list = [input_data]
    elif isinstance(input_data, list):
        # 过滤非字符串元素（避免类型错误）
        check_list = [item for item in input_data if isinstance(item, str)]
    else:
        print("入参仅支持字符串或字符串列表")
        return False
    
    for code in check_list:
        if not bool(pattern.match(code)):
            print(f"股票代码格式错误: {code}（需6位数字+市场后缀，如688318.SH）")
            return False
    
    return True

def is_callback_func(func):
    """
    判断入参是否为 on_data(datas) 格式的函数
    """
    # 校验是否为可调用对象
    if not callable(func):
        return False
    
    try:
        # 获取函数的参数签名
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        
        # 筛选必填参数（无默认值、非*/*kwargs的参数）
        required_params = []
        for param in params:
            # 排除可变位置参数(*args)、可变关键字参数(**kwargs)
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            if param.default is inspect.Parameter.empty:
                required_params.append(param)
        
        # 校验必填参数数量为1（核心规则）
        if len(required_params) != 1:
            return False
        return True
    
    except (ValueError, TypeError):
        return False

class tq:
    """TDX数据访问类，提供市场数据获取接口"""

    # 类变量，存储连接路径和资源
    _connection_path: str = ''
    _initialized = False

    run_id = -1
    run_mode = -1
    file_name = __file__

    # 添加finalizer相关
    _finalizer = None

    #是否已经将外套回调函数注册
    m_is_init_data_transfer = False
    #外套回调函数
    data_transfer = ctypes.CFUNCTYPE(None, ctypes.c_char_p)
    #订阅回调函数{run_id: {code: callback_func}}
    data_callback_func = defaultdict(dict)
    # 缓存前复权因子
    _forward_factor_cache = {}

    # 订阅股票的列表
    _sub_hq_update = []

    @classmethod
    def _release(cls):
        if cls._initialized:
            dll.CloseConnect(cls.run_id, cls.run_mode)
            cls._initialized = False

    @classmethod
    def initialize(cls, path:str):
        cls._connection_path = path
        cls._auto_initialize()

        # 注册finalizer（如果尚未注册）
        if cls._finalizer is None:
            cls._finalizer = weakref.finalize(cls, cls._auto_close)
            # 同时注册atexit确保程序退出时清理
            atexit.register(cls._auto_close)

    @classmethod
    def _auto_close(cls):
        """自动关闭连接（线程安全版本）"""
        if cls._initialized:
            try:
                dll.CloseConnect(cls.run_id, cls.run_mode)
                cls._initialized = False
                print("TDX数据连接已自动关闭")
            except Exception as e:
                print(f"自动关闭连接时出错: {e}")

    @classmethod
    def close(cls):
        """手动关闭连接"""
        cls._auto_close()
        
        # 清理finalizer
        if cls._finalizer is not None and cls._finalizer.alive:
            cls._finalizer()

    # 析构方法
    def __del__(self):
        """实例析构时检查是否需要关闭类连接"""
        # 确保atexit已注册
        if not hasattr(tq, '_atexit_registered'):
            atexit.register(tq._auto_close)
            tq._atexit_registered = True
    
    @classmethod
    def _ensure_cleanup_registered(cls):
        """确保清理机制已注册"""
        if cls._finalizer is None:
            cls._finalizer = weakref.finalize(cls, cls._auto_close)
            atexit.register(cls._auto_close)
            # 设置标记，避免重复注册
            cls._atexit_registered = True
            # print("资源清理机制已注册") 

    @classmethod
    def _get_run_id(cls) -> int:
        """
        获取当前的run_id
        """
        if cls._initialized:
            return cls.run_id
        else:
            cls.close()
            raise RuntimeError("TDX数据接口未正确初始化")

    @classmethod
    def _auto_initialize(cls):
        """自动初始化连接"""
        if not cls._initialized:
            # 确保清理机制已注册
            cls._ensure_cleanup_registered()

            if len(cls._connection_path) <= 0:
                raise RuntimeError("TDX数据接口初始化失败。")
            try:
                arguments = sys.argv[1:]
                if len(arguments) == 2:
                    if arguments[0] == '--run_tdx':
                        cls.run_mode = int(arguments[1])
                cls.file_name = cls._connection_path.encode('utf-8')
                ptr = dll.InitConnect(cls.file_name, cls.run_mode, get_python_version_number())
                if len(ptr) <= 0:
                    raise RuntimeError("TDX数据接口初始化失败:启动TPythClient失败。")
                else:
                    ptr = ptr.decode('utf-8')
                    ptr_json = json.loads(ptr)
                    if ptr_json.get('ErrorId') == '0' or ptr_json.get('ErrorId') == '12':
                        cls.run_id = int(ptr_json.get('run_id', '-1'))
                        if ptr_json.get('ErrorId') == '12':
                            print(ptr_json.get('Error'))
                    else:
                        cls.run_id = -1
                if cls.run_id < 0:
                    raise RuntimeError("TDX数据接口初始化失败或已有同名策略运行。")
                cls._initialized = True
                print(f"TDX数据接口自动初始化成功，使用路径: {cls._connection_path}")
            except Exception as e:
                raise RuntimeError("TDX数据接口初始化失败。")

            if not cls._initialized:
                raise RuntimeError(
                    "TDX数据接口自动初始化失败。请手动调用 tq.initialize(path) 初始化连接。\n"
                    "可能的路径包括：当前目录、上级目录或空字符串。"
                )

    @classmethod
    def _format_kline_data(cls,
                           all_data: Dict,
                           stock_list: List[str],
                           fill_data: bool) -> Dict:
        """
        格式化K线数据
        """
        if not all_data:
            return {}

        # 确定所有字段
        available_fields = set()
        for stock_data in all_data.values():
            available_fields.update(stock_data.keys())
        selected_fields = list(available_fields)

        # 移除非数据字段
        non_data_fields = {'ErrorId'}
        available_fields = available_fields - non_data_fields

        # 确定时间索引（所有股票数据的并集）
        all_timestamps = set()
        for stock_data in all_data.values():
            if 'Date' in stock_data:
                dates = stock_data['Date']
                times = stock_data.get('Time', [])
                
                for i, date in enumerate(dates):
                    if i < len(times) and times[i] not in ["0", "000000", "0000"]:
                        # 分钟线数据：结合Date和Time
                        time_str = f"{int(times[i]):06d}"
                        timestamp = f"{date}{time_str}"
                    else:
                        # 日线数据：只使用Date
                        timestamp = date
                    all_timestamps.add(timestamp)

        if not all_timestamps:
            return {}

        # 转换为datetime索引
        def parse_timestamp(ts):
            if len(ts) == 8:  # YYYYMMDD
                return datetime.strptime(ts, '%Y%m%d')
            else:  # YYYYMMDDHHMMSS
                return datetime.strptime(ts, '%Y%m%d%H%M%S')
        
        time_index = pd.DatetimeIndex([parse_timestamp(ts) for ts in sorted(all_timestamps)])

        # 创建结果字典
        result = {}

        for field in selected_fields:
            # 创建DataFrame，index为时间，columns为股票代码
            df = pd.DataFrame(index=time_index, columns=stock_list, dtype=float)

            for stock in stock_list:
                if stock in all_data and field in all_data[stock]:
                    stock_field_data = all_data[stock][field]
                    stock_dates = all_data[stock].get('Date', [])
                    stock_times = all_data[stock].get('Time', [])

                    # 构建完整的时间戳索引
                    stock_timestamps = []
                    for i, date in enumerate(stock_dates):
                        if i < len(stock_times) and stock_times[i] not in ["0", "000000", "0000"]:
                            time_str = f"{int(stock_times[i]):06d}"
                            stock_timestamps.append(f"{date}{time_str}")
                        else:
                            stock_timestamps.append(date)

                    # 转换为datetime
                    stock_datetimes = []
                    for ts in stock_timestamps:
                        if len(ts) == 8:  # 只有日期
                            dt = datetime.strptime(ts, '%Y%m%d')
                        else:  # 包含时间
                            dt = datetime.strptime(ts, '%Y%m%d%H%M%S')
                        stock_datetimes.append(dt)

                    # 创建临时Series来对齐数据
                    if len(stock_datetimes) == len(stock_field_data):
                        temp_series = pd.Series(
                            [float(x) if x else np.nan for x in stock_field_data],
                            index=pd.DatetimeIndex(stock_datetimes)
                        )
                        # 重新索引以对齐时间轴
                        temp_series = temp_series.reindex(time_index)

                        # 填充数据
                        if fill_data:
                            temp_series = temp_series.ffill()  # 向前填充

                        # 将数据放入DataFrame
                        df[stock] = temp_series.values

            result[field] = df

        return result

    @classmethod
    def _format_tick_data(cls, all_data: Dict, field_list: List[str]) -> Dict:
        """
        格式化tick数据
        """
        result = {}

        for stock, stock_data in all_data.items():
            # 对于tick数据，返回结构化数组
            if 'Date' in stock_data and 'Time' in stock_data:
                dates = stock_data['Date']
                times = stock_data['Time']

                # 创建时间戳
                timestamps = []
                for date, time in zip(dates, times):
                    if time == "0":
                        dt_str = f"{date}000000"
                    else:
                        dt_str = f"{date}{int(time):06d}"
                    timestamps.append(dt_str)

                # 确定要包含的字段
                available_fields = list(stock_data.keys())
                if field_list:
                    selected_fields = [f for f in field_list if
                                       f in available_fields and f not in ['Date', 'Time', 'ErrorId']]
                else:
                    selected_fields = [f for f in available_fields if f not in ['Date', 'Time', 'ErrorId']]

                # 创建结构化数组
                dtype = [('datetime', 'U14')]
                for field in selected_fields:
                    # 根据数据类型确定dtype
                    sample_value = stock_data[field][0] if stock_data[field] else "0"
                    if '.' in sample_value:
                        dtype.append((field, float))
                    else:
                        dtype.append((field, int))

                # 创建数组
                data_count = len(timestamps)
                if data_count > 0:
                    arr = np.zeros(data_count, dtype=dtype)
                    arr['datetime'] = timestamps

                    for field in selected_fields:
                        if field in stock_data and len(stock_data[field]) == data_count:
                            try:
                                if dtype[selected_fields.index(field) + 1][1] == float:
                                    arr[field] = [float(x) if x else 0.0 for x in stock_data[field]]
                                else:
                                    arr[field] = [int(float(x)) if x else 0 for x in stock_data[field]]
                            except (ValueError, TypeError):
                                arr[field] = stock_data[field]

                    result[stock] = arr

        return result

    # ======== 数据提取与准备 ========
    @staticmethod
    def price_df(df, price_col, column_names=None):
        if not isinstance(df, dict) or len(df) == 0:
            tq.close()
            raise ValueError(f"输入数据为空（类型：{type(df)}）")

        if price_col not in df:
            tq.close()
            available_fields = list(df.keys())
            raise ValueError(f"数据中不存在'{price_col}'字段！\n可用字段：{available_fields}")

        # 直接获取对应字段的DataFrame
        df_price = df[price_col].copy()

        # 确保索引是datetime类型
        if not isinstance(df_price.index, pd.DatetimeIndex):
            df_price.index = pd.to_datetime(df_price.index)

        # 排序索引
        df_price = df_price.sort_index()

        # 转换为数值类型
        df_price = df_price.apply(pd.to_numeric, errors='coerce')

        # 填充缺失值
        df_price = df_price.ffill().bfill()

        if df_price.isnull().any().any():
            null_cols = df_price.columns[df_price.isnull().any()].tolist()
            print(f"警告：价格数据存在无法填充的空值（股票：{null_cols}）")

        # 重命名列
        if column_names is not None and len(column_names) == len(df_price.columns):
            df_price.columns = column_names
        elif column_names is not None:
            print(f"警告：自定义列名数量（{len(column_names)}）与数据列数（{len(df_price.columns)}）不匹配")

        return df_price

    @classmethod
    def _add_forward_factor_to_data(cls, data_dict: Dict, stock_list: List[str]) -> Dict:
        """
        为行情数据添加前复权因子
        """
        if not data_dict:
            return data_dict

        # 获取第一个字段的DataFrame作为时间索引参考
        first_field = next(iter(data_dict.keys()))
        time_index = data_dict[first_field].index

        # 为每只股票计算前复权因子
        for stock in stock_list:
            try:
                # 计算该股票的前复权因子
                daily_factors = cls._calculate_stock_forward_factors(stock, time_index)

                # 添加到数据字典中
                if 'ForwardFactor' not in data_dict:
                    data_dict['ForwardFactor'] = pd.DataFrame(index=time_index, columns=stock_list)

                data_dict['ForwardFactor'][stock] = daily_factors

            except Exception as e:
                print(f"为 {stock} 计算前复权因子失败: {e}")
                # 如果计算失败，使用默认因子1.0
                if 'ForwardFactor' not in data_dict:
                    data_dict['ForwardFactor'] = pd.DataFrame(index=time_index, columns=stock_list)
                data_dict['ForwardFactor'][stock] = 1.0
                continue

        return data_dict

    @classmethod
    def _calculate_stock_forward_factors(cls, stock_code: str, time_index: pd.DatetimeIndex) -> pd.Series:
        """
        计算单只股票的前复权因子
        关键原则：
        1. 最新日期的前复权因子始终为1.0
        2. 除权除息事件只影响事件发生日之前的历史数据
        3. 事件发生日当天的前复权因子保持不变
        """
        # 检查缓存
        cache_key = f"{stock_code}_forward_factors"
        if cache_key in cls._forward_factor_cache:
            cached_factors = cls._forward_factor_cache[cache_key]
            # 返回对应时间范围的因子
            return cached_factors.reindex(time_index).ffill().bfill()

        try:
            # 获取该股票的除权除息数据（使用较长时间范围）
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (time_index.min() - pd.Timedelta(days=365 * 5)).strftime('%Y%m%d')  # 5年数据

            df_factors = cls.get_divid_factors(stock_code, start_date, end_date)
            if df_factors.empty:
                print(f"警告：无法获取 {stock_code} 的除权除息数据，使用默认因子1.0")
                return pd.Series(1.0, index=time_index)

            # 获取不复权价格数据用于计算
            price_data = cls.get_market_data(
                field_list=['Close'],
                stock_list=[stock_code],
                start_time=start_date,
                end_time=end_date,
                period='1d',
                dividend_type='none'
            )

            if not price_data or 'Close' not in price_data:
                print(f"警告：无法获取 {stock_code} 的价格数据，使用默认因子1.0")
                return pd.Series(1.0, index=time_index)

            # 提取价格数据
            price_series = cls.price_df(price_data, 'Close')[stock_code]

            # 计算前复权因子的调整系数
            forward_factors = cls._calculate_forward_factors_from_dividends(df_factors, price_series)

            # 创建每日因子序列
            daily_factors = pd.Series(index=time_index, dtype=float)

            # 从最新日期向前填充因子
            # 确保最新日期的ForwardFactor为1.0
            latest_factor = 1.0
            daily_factors.iloc[-1] = latest_factor  # 最新日期的因子为1.0

            # 遍历除了最新日期的所有日期（从倒数第二个日期开始向前）
            for i in reversed(range(len(time_index) - 1)):
                current_date = time_index[i]
                next_date = time_index[i + 1]  # 下一个交易日

                # 检查当前日期是否有除权除息事件
                if current_date in forward_factors.index:
                    # 当前日期是除权除息事件发生日
                    # 事件发生日当天的因子与下一个交易日相同
                    daily_factors.iloc[i] = latest_factor
                else:
                    # 检查下一个交易日是否有除权除息事件
                    if next_date in forward_factors.index:
                        # 下一个交易日是除权除息事件发生日
                        # 当前日期的因子 = 下一个交易日的因子 * 调整系数
                        adjustment_factor = forward_factors.loc[next_date]
                        daily_factors.iloc[i] = latest_factor * adjustment_factor
                    else:
                        # 当前日期的因子与下一个交易日相同
                        daily_factors.iloc[i] = latest_factor

                # 更新最新因子值
                latest_factor = daily_factors.iloc[i]

            # 缓存结果
            cls._forward_factor_cache[cache_key] = daily_factors

            return daily_factors.round(6)

        except Exception as e:
            print(f"计算 {stock_code} 前复权因子异常: {e}")
            import traceback
            traceback.print_exc()
            return pd.Series(1.0, index=time_index)

    @classmethod
    def _calculate_forward_factors_from_dividends(cls, df_factors: pd.DataFrame, price_series: pd.Series) -> pd.Series:
        """
        从除权除息数据计算前复权因子的调整系数
        返回的是从旧到新的调整系数，键为事件发生日期
        """
        if df_factors.empty or price_series.empty:
            return pd.Series()

        # 按日期正序排列（从旧到新）
        df_sorted = df_factors.sort_index(ascending=True).copy()

        # 初始化调整系数字典
        adjust_dict = {}

        # 获取价格数据的所有日期
        price_dates = price_series.index

        # 遍历所有除权除息事件
        for date in df_sorted.index:
            if date not in price_dates:
                continue

            row = df_sorted.loc[date]

            # 获取前一日的价格
            prev_date_idx = price_dates.get_loc(date) - 1
            if prev_date_idx < 0:
                continue

            prev_date = price_dates[prev_date_idx]
            prev_close = price_series.iloc[prev_date_idx]

            if prev_close <= 0:
                continue

            # 提取分红送股信息
            bonus_per_10 = row['Bonus']  # 每10股分红
            bonus_per_share = bonus_per_10 / 10.0  # 每股分红
            share_bonus_ratio = row['ShareBonus'] / 10.0  # 送股比例
            allotment_ratio = row['Allotment'] / 10.0  # 配股比例
            allot_price = row['AllotPrice']  # 配股价

            # 计算除权除息价
            # 除权价 = (前收盘价 - 现金分红) / (1 + 送股比例 + 转增比例)
            denominator = 1 + share_bonus_ratio + allotment_ratio
            if denominator <= 0:
                denominator = 1.0

            ex_right_price = (prev_close - bonus_per_share) / denominator

            # 计算调整系数
            # 调整系数 = 除权除息价 / 前收盘价
            adjust_ratio = ex_right_price / prev_close

            # 将调整系数关联到事件发生日期
            adjust_dict[date] = adjust_ratio

        # 创建调整系数序列
        adjust_series = pd.Series(adjust_dict)

        return adjust_series.sort_index()
    
    @classmethod
    def _data_callback_transfer(cls, data_str):
        data_str = data_str.decode('utf-8')
        data_json = json.loads(data_str)
        codes = data_json['Code']

        if cls.data_callback_func.get(cls._get_run_id()) is None:
            print("No callback function registered for run_id:", cls._get_run_id())
            return None
        if cls.data_callback_func[cls._get_run_id()].get(codes) is None:
            print("No callback function registered for code:", codes)
            return None
        return cls.data_callback_func[cls._get_run_id()][codes](data_str)
    
    @classmethod
    def _financial_transfer(cls, data_str)->Dict:
        """将C++接口的财务数据转换为指定格式的字典"""
        result = {}
        for key, value in data_str.items():
            # 跳过非表格数据，比如 'ErrorId'
            if key == 'ErrorId' or not isinstance(value, dict):
                continue
            
            try:
                df = pd.DataFrame(value)
                result[key] = df
            except Exception as e:
                print(f"构建表 '{key}' 的DataFrame时出错: {e}")
                continue

        return result
        
    @classmethod
    def filter_dict_by_fields(cls, data: Dict = {}, field_list: List = []) -> Dict:
        """
        根据指定的字段列表筛选字典中的键值对（不区分大小写）

        Args:
            data: 原始字典数据
            field_list: 需要保留的字段列表（大小写不敏感）
            
        Returns:
            筛选后的新字典（保留原始键名的大小写）
        """
        # 创建小写键到原始键的映射
        key_lower_map = {key.lower(): key for key in data.keys()}

        # 筛选字段（不区分大小写）
        filtered_data = {}
        for field in field_list:
            field_lower = field.lower()
            if field_lower in key_lower_map:
                original_key = key_lower_map[field_lower]
                filtered_data[original_key] = data[original_key]

        return filtered_data
    
    @classmethod
    def get_market_data(cls,
                        field_list: List[str] = [],
                        stock_list: List[str] = [],
                        period: str = '',
                        start_time: str = '',
                        end_time: str = '',
                        count: int = -1,
                        dividend_type: Optional[str] = None,  # 改为Optional类型
                        fill_data: bool = True) -> Dict:

        # 自动初始化连接（如果尚未初始化）
        cls._auto_initialize()

        # 必填入参检查
        if not stock_list:
            cls.close()
            raise ValueError("必传参数缺失：stock_list不能为空，请提供合约代码列表")

        if not period:
            cls.close()
            raise ValueError(
                "必传参数缺失：period不能为空，请指定数据周期（如'1d','1m','5m','15m','30m','60m','1w','tick'等）")

        # 时间参数检查：count<0时必须提供起始和结束时间
        # if count < 0:
        #     if not start_time:
        #         raise ValueError("必传参数缺失：start_time不能为空，当count<0时必须指定起始时间")
        #     if not end_time:
        #         raise ValueError("必传参数缺失：end_time不能为空，当count<0时必须指定结束时间")

        # 如果未传入dividend_type，默认为'none'
        if dividend_type is None:
            dividend_type = 'none'

        # 转换除权类型
        dividend_type_map = {
            'none': 0,  # 不复权（默认）
            'front': 1,  # 前复权
            'back': 2  # 后复权
        }
        # 统一转为小写处理，增强容错性
        dividend_type_int = dividend_type_map.get(dividend_type.lower(), 0)

        # 股票代码格式校验
        if not check_stock_code_format(stock_list):
            tq.close()
            raise ValueError(f"{stock_list}异常")
        # valid_codes = []
        # for code in stock_list:
        #     if not isinstance(code, str) or (len(code) not in [6, 8] and '.' not in code):
        #         return {'error': -2, 'msg': f'股票代码格式错误：{code}（应为6位数字或带市场后缀如600000.SH）'}
        #     valid_codes.append(code)

        # 周期校验
        valid_periods = ['5m', '15m', '30m', '1h', '1d', '1w', '1mon', '1m', '10m', '45d', '1q', '1y']
        if period.lower() not in valid_periods:
            return {'error': -5, 'msg': f'周期格式错误：{period}（支持{valid_periods}）'}

        if count >= 0 and not end_time:
            # 如果没有指定end_time，使用当前时间
            end_time = datetime.now().strftime('%Y%m%d%H%M%S')

        # 格式化时间参数
        if start_time:
            start_time = _convert_time_format(start_time)
        if end_time:
            end_time = _convert_time_format(end_time)

        # 获取所有股票的数据
        all_data = {}

        for stock in stock_list:
            # 直接调用底层DLL接口获取单只股票数据
            codestr = stock.encode('utf-8')
            startimestr = start_time.encode('utf-8')
            endtimestr = end_time.encode('utf-8')
            periodstr = period.encode('utf-8')
            timeout_ms = 10000  # 10秒超时

            try:
                run_id = cls._get_run_id()
                ptr = dll.GetHISDATsInStr(
                    run_id,
                    codestr,
                    startimestr,
                    endtimestr,
                    periodstr,
                    dividend_type_int,
                    count,
                    timeout_ms
                )
                

                # 检查返回的指针
                if ptr is None or ptr == 0:
                    print(f"获取{stock}数据失败: 返回空指针")
                    continue

                # 解析JSON数据
                try:
                    data_dict = json.loads(ptr)
                except json.JSONDecodeError as e:
                    print(f"获取{stock}数据失败: JSON解析错误 - {e}")
                    print(f"原始返回数据: {ptr}")
                    continue

                # 检查错误代码
                if data_dict.get("ErrorId") != "0":
                    print(f"获取{stock}数据错误: {data_dict.get('ErrorId')}")
                    print(f"错误信息: {data_dict.get('Error')}")
                    continue

                all_data[stock] = data_dict
                

            except Exception as e:
                print(f"获取{stock}数据异常: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # stime = time.time()
        # 根据周期类型格式化返回数据
        if period == 'tick':
            result_data = cls._format_tick_data(all_data, field_list)
        else:
            result_data = cls._format_kline_data(all_data, stock_list, fill_data) #格式化K线数据但是还没筛选field_list
        
        # etime = time.time()
        # print(f"数据格式化耗时: {etime - stime:.4f}秒")

        # 筛选字段
        if field_list:
            available = set(result_data.keys())
            selected = [f for f in field_list if f in available]
            return {f: result_data[f].copy() for f in selected}
        else:
        # 如果没有提供 field_list，则排除 ErrorId 字段
            return {k: v.copy() for k, v in result_data.items() if k != "ErrorId"}

        # 添加前复权因子（仅当field_list为空或包含'ForwardFactor'时）
        # if period != 'tick':
        #     # 检查是否需要添加ForwardFactor字段
        #     if not field_list or 'ForwardFactor' in field_list:
        #         result_data = cls._add_forward_factor_to_data(result_data, stock_list)
        #     # 筛选字段
        #     if field_list:
        #         available = set(result_data.keys())
        #         selected = [f for f in field_list if f in available]
        #         return {f: result_data[f].copy() for f in selected}
        #     else:
        #     # 如果没有提供 field_list，则排除 ErrorId 字段
        #         return {k: v.copy() for k, v in result_data.items() if k != "ErrorId"}
        
        return result_data

    @classmethod
    def get_divid_factors(cls,
                          stock_code: str,
                          start_time: str,
                          end_time: str) -> pd.DataFrame:
        """获取除权除息数据"""
        cls._auto_initialize()

        # 参数验证
        if not stock_code:
            return pd.DataFrame()

        if not end_time:
            end_time = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # 格式化时间参数
        if start_time:
            start_time = _convert_time_format(start_time)
        if end_time:
            end_time = _convert_time_format(end_time)

        # 准备参数
        codestr = stock_code.encode('utf-8')
        startimestr = start_time.encode('utf-8')
        endtimestr = end_time.encode('utf-8')
        timeout_ms = 5000

        # 调用DLL函数 - 直接返回字符串
        result_str = dll.GetCWDATAInStr(cls._get_run_id(), codestr, startimestr, endtimestr, timeout_ms)

        # 检查返回结果
        if result_str is None or len(result_str) == 0:
            return pd.DataFrame()

        # 解码字符串
        try:
            result_str = result_str.decode('utf-8')
        except Exception:
            return pd.DataFrame()

        # 解析JSON数据
        try:
            data_dict = json.loads(result_str)

            if data_dict.get("ErrorId") != "0":
                return pd.DataFrame()

            # 提取数据
            dates = data_dict.get("Date", [])
            types = data_dict.get("Type", [])
            values = data_dict.get("Value", [])

            if not dates:
                return pd.DataFrame()

            # 创建DataFrame
            bonus_list = []
            allot_price_list = []
            share_bonus_list = []
            allotment_list = []

            for value_item in values:
                if value_item and len(value_item) >= 4:
                    bonus_list.append(float(value_item[0]) if value_item[0] else 0.0)
                    allot_price_list.append(float(value_item[1]) if value_item[1] else 0.0)
                    share_bonus_list.append(float(value_item[2]) if value_item[2] else 0.0)
                    allotment_list.append(float(value_item[3]) if value_item[3] else 0.0)
                else:
                    bonus_list.append(0.0)
                    allot_price_list.append(0.0)
                    share_bonus_list.append(0.0)
                    allotment_list.append(0.0)

            df = pd.DataFrame({
                'Date': dates,
                'Type': types,
                'Bonus': bonus_list,
                'AllotPrice': allot_price_list,
                'ShareBonus': share_bonus_list,
                'Allotment': allotment_list
            })

            # 处理日期和索引
            df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d', errors='coerce')
            df = df.dropna(subset=['Date'])  # 删除无效日期
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)

            # 根据时间区间进行切片 C接口的时间没有实际作用，返回的是所有权息数据
            start_ts = pd.Timestamp(start_time, tz=None)   # 与索引保持 naive 一致
            end_ts = pd.Timestamp(end_time, tz=None)
            if not start_time:
                mask = (df.index <= end_ts)
            else:
                mask = (df.index >= start_ts) & (df.index <= end_ts)
            df = df.loc[mask].copy()

            return df

        except json.JSONDecodeError:
            return pd.DataFrame()
    
    @classmethod
    def get_stock_info(cls,
                        stock_code:str, 
                        field_list: List = []) -> Dict:
        """获取基础财务数据"""
        # 自动初始化连接
        cls._auto_initialize()

        if not check_stock_code_format(stock_code):
            tq.close()
            raise ValueError(f"{stock_code}异常")
        codestr = stock_code.encode('utf-8')
        timeout_ms = 5000

        try:
            ptr = dll.GetSTOCKInStr(cls._get_run_id(), codestr, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("获取合约详情失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"获取合约详情错误: {json_res.get('Error')}")
            if field_list:
                json_res = cls.filter_dict_by_fields(json_res, field_list)
            return json_res
        except Exception as e:
            cls.close()
            raise ValueError("获取合约详情异常")
        
    @classmethod
    def get_full_tick(cls,
                    stock_code: str) -> Dict:
        """获取报表数据"""
        # 自动初始化连接
        cls._auto_initialize()
        
        if not check_stock_code_format(stock_code):
            tq.close()
            raise ValueError(f"{stock_code}异常")
        codestr = stock_code.encode('utf-8')
        timeout_ms = 50000

        try:
            ptr = dll.GetREPORTInStr(cls._get_run_id(), codestr, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("获取报表数据失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"获取报表数据错误: {json_res.get('Error')}")
            return json_res
        except Exception as e:
            cls.close()
            raise ValueError("获取报表数据异常")
        
    @classmethod
    def send_message(cls,
                    msg_str: str) -> Dict:
        """策略管理输出字符串"""
        # 自动初始化连接
        cls._auto_initialize()

        msg_str = 'MSG||' + msg_str
        resultstr = msg_str.encode('utf-8')
        timeout_ms = 5000

        try:
            ptr = dll.SetResToMain(cls._get_run_id(), cls.run_mode, resultstr, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("发送信息到主程序失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"发送信息到主程序错误: {json_res.get('Error')}")
            return json_res
        except Exception as e:
            cls.close()
            raise ValueError("发送信息到主程序异常")

    @classmethod
    def send_file(cls,
                    file_path: str) -> Dict:
        """策略管理输出字符串"""
        # 自动初始化连接
        cls._auto_initialize()

        file_path = 'FILE||' + file_path
        resultstr = file_path.encode('utf-8')
        timeout_ms = 10000

        try:
            ptr = dll.SetResToMain(cls._get_run_id(), cls.run_mode, resultstr, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("发送文件路径到主程序失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"发送文件路径到主程序错误: {json_res.get('Error')}")
            return json_res
        except Exception as e:
            cls.close()
            raise ValueError("发送文件路径到主程序异常")

    @classmethod
    def send_warn(cls,
                  stock_list:        List[str] = [],
                  time_list:         List[str] = [],
                  price_list:        List[str] = [],
                  close_list:        List[str] = [],
                  volum_list:        List[str] = [],
                  bs_flag_list:      List[str] = [],
                  warn_type_list:    List[str] = [],
                  reason_list:       List[str] = [],
                  count:        int  = 1) -> Dict:
        """策略管理输出字符串"""
        if count <= 0:
            cls.close()
            raise ValueError("发送预警参数错误：count必须大于0")

        # 自动初始化连接
        cls._auto_initialize()

        if not check_stock_code_format(stock_list):
            tq.close()
            raise ValueError(f"{stock_list}异常")

        warn_str = get_warn_struct_str(stock_list,
                                       time_list,
                                       price_list,
                                       close_list,
                                       volum_list,
                                       bs_flag_list,
                                       warn_type_list,
                                       reason_list,
                                       count)
        warn_str = 'WARN||' + warn_str
        warn_str = warn_str.encode('utf-8')
        timeout_ms = 10000

        try:
            ptr = dll.SetResToMain(cls._get_run_id(), cls.run_mode, warn_str, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("发送预警信息到主程序失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"发送预警信息到主程序错误: {json_res.get('Error')}")
            return json_res
        except Exception as e:
            cls.close()
            raise ValueError("发送预警信息到主程序异常")

    @classmethod
    def send_bt_data(cls,
                     stock_code:          str  = '',
                     time_list:         List[str] = [],
                     data_list:         List[List[str]] = [],
                     count:        int  = 1) -> Dict:
        """策略管理输出回测数据"""
        if count <= 0:
            cls.close()
            raise ValueError("发送回测数据错误：count必须大于0")
        if not check_stock_code_format(stock_code):
            tq.close()
            raise ValueError(f"{stock_code}异常")
        # 自动初始化连接
        cls._auto_initialize()

        bt_data = get_bt_struct_str(time_list,
                                    data_list,
                                    count)  
        bt_data = 'BTR||' + stock_code + '||' + bt_data
        bt_data = bt_data.encode('utf-8')
        timeout_ms = 100000

        try:
            ptr = dll.SetResToMain(cls._get_run_id(), cls.run_mode, bt_data, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("发送回测数据到主程序失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"发送回测数据到主程序错误: {json_res.get('Error')}")
            return json_res
        except Exception as e:
            cls.close()
            raise ValueError("发送回测数据到主程序异常")

    @classmethod
    def send_user_block(cls,
                block_code: str = '',
                stocks: List[str] = []) -> Dict:
        """客户端添加自选股"""
        # 自动初始化连接
        cls._auto_initialize()

        result_str = convert_or_validate(stocks)
        # if not result_str:
        #     cls.close()
        #     raise ValueError("自选股格式错误")

        result_str = 'XG,' + block_code + '||' + result_str
        resultstr = result_str.encode('utf-8')
        timeout_ms = 5000

        try:
            ptr = dll.SetResToMain(cls._get_run_id(), cls.run_mode, resultstr, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("发送自选股到主程序失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"发送自选股到主程序错误: {json_res.get('Error')}")
            return json_res
        except Exception as e:
            cls.close()
            raise ValueError("发送自选股到主程序异常")

    @classmethod
    def get_sector_list(cls) -> List:
        """获取板块列表"""
        # 自动初始化连接
        cls._auto_initialize()

        timeout_ms = 5000

        try:
            ptr = dll.GetBlockListInStr(cls._get_run_id(), timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("获取板块列表失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"获取板块列表错误: {json_res.get('Error')}")
            result = [item.replace('.1', '.SH').replace('.0', '.SZ').replace('.2', '.BJ') for item in json_res['Value']]
            return result
        except Exception as e:
            cls.close()
            raise ValueError("获取板块列表异常")
        
    @classmethod
    def get_stock_list_in_sector(cls,
                         block_code: str,
                         block_type: int = 0) -> List:
        """获取板块成分股"""
        # 自动初始化连接
        cls._auto_initialize()

        if block_type == 1:
            block_code  = "BKCODE." + block_code
        codestr = block_code.encode('utf-8')
        timeout_ms = 5000

        try:
            ptr = dll.GetBlockStocksInStr(cls._get_run_id(), codestr, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("获取板块成分股失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"获取板块成分股错误: {json_res.get('Error')}")
            
            result = [item.replace('.1', '.SH').replace('.0', '.SZ').replace('.2', '.BJ') for item in json_res['Value']]
            return result
        except Exception as e:
            cls.close()
            raise ValueError("获取板块成分股异常")

    @classmethod
    def get_financial_data(cls,
                            stock_list: List[str] = [], 
                            field_list: List[str] = [], 
                            start_time: str = '', 
                            end_time: str = '', 
                            report_type: str = 'report_time') -> Dict:
        """获取财务数据"""
        # 自动初始化连接
        cls._auto_initialize()
        # 必填入参检查
        if not stock_list:
            cls.close()
            raise ValueError("必传参数缺失：stock_list不能为空，请提供合约代码列表")
        
        if not check_stock_code_format(stock_list):
            tq.close()
            raise ValueError(f"{stock_list}异常")

        if not end_time:
            end_time = datetime.now().strftime('%Y%m%d%H%M%S')

        # 格式化时间参数
        if start_time:
            start_time = _convert_time_format(start_time)
        if end_time:
            end_time = _convert_time_format(end_time)

        timeout_ms = 60000 # 60秒超时
        result_dict = {}    # 返回结果字典

        for stock in stock_list:
            try:
                stock_json = {  "id" : cls._get_run_id(),
                                "type": "1",
                                "code": stock,
                                "table_list": field_list,
                                "start_time": start_time,
                                "end_time": end_time,
                                "report_type": report_type}
                json_str = json.dumps(stock_json, ensure_ascii=False)
                json_str = json_str.encode('utf-8')
                ptr = dll.GetProDataInStr(cls._get_run_id(),json_str,timeout_ms)
                # 检查返回的指针
                if ptr is None or len(ptr) == 0:
                    print(f"获取{stock}财务数据失败: 返回空指针")
                    continue

                # 解析JSON数据
                try:
                    data_dict = json.loads(ptr)
                except json.JSONDecodeError as e:
                    print(f"获取{stock}财务数据失败: JSON解析错误 - {e}")
                    print(f"原始返回数据: {ptr}")
                    continue

                # 检查错误代码
                if data_dict.get("ErrorId") != "0":
                    print(f"获取{stock}财务数据错误: {data_dict.get('Error')}")
                    continue

                # converted = dynamic_qmt_converter(data_dict)  
                # merged = merge_all_statements(converted) 
                
                # 转换为指定格式
                # formatted_data = cls._financial_transfer(data_dict['Data'])
                # result_dict[stock] = formatted_data

                # 获取所有列表的长度，检查是否一致
                list_lengths = [len(v) for v in data_dict['Data'].values()]
                if len(set(list_lengths)) != 1:
                    tq.close()
                    raise ValueError(f"输入字典中各字段的列表长度不一致，返回当前数据：{data_dict['Data']}")
                
                # 2. 转换为DataFrame
                df = pd.DataFrame(data_dict['Data'])
                result_dict[stock] = df

            except Exception as e:
                print(f"获取{stock}财务数据异常: {e}")
                import traceback
                traceback.print_exc()
                continue

        return result_dict
    
    @classmethod
    def get_financial_data_by_date(cls,
                                    stock_list: List[str] = [], 
                                    field_list: List[str] = [],  
                                    year: int = 0,
                                    mmdd: int = 0) -> Dict:
        """获取财务数据"""
        # 自动初始化连接
        cls._auto_initialize()
        # 必填入参检查
        if not stock_list:
            cls.close()
            raise ValueError("必传参数缺失：stock_list不能为空，请提供合约代码列表")
        
        if not check_stock_code_format(stock_list):
            tq.close()
            raise ValueError(f"{stock_list}异常")

        timeout_ms = 60000 # 60秒超时
        result_dict = {}    # 返回结果字典

        for stock in stock_list:
            try:
                stock_json = {  "id" : cls._get_run_id(),
                                "type": "2",
                                "code": stock,
                                "table_list": field_list,
                                "year": year,
                                "mmdd": mmdd}
                json_str = json.dumps(stock_json, ensure_ascii=False)
                json_str = json_str.encode('utf-8')
                ptr = dll.GetProDataInStr(cls._get_run_id(),json_str,timeout_ms)
                # 检查返回的指针
                if ptr is None or len(ptr) == 0:
                    print(f"获取{stock}财务数据失败: 返回空指针")
                    continue

                # 解析JSON数据
                try:
                    data_dict = json.loads(ptr)
                except json.JSONDecodeError as e:
                    print(f"获取{stock}财务数据失败: JSON解析错误 - {e}")
                    print(f"原始返回数据: {ptr}")
                    continue

                # 检查错误代码
                if data_dict.get("ErrorId") != "0":
                    print(f"获取{stock}财务数据错误: {data_dict.get('Error')}")
                    continue

                result_dict[stock] = data_dict['Data']

            except Exception as e:
                print(f"获取{stock}财务数据异常: {e}")
                import traceback
                traceback.print_exc()
                continue

        return result_dict
    
    @classmethod
    def get_gpjy_value(cls,
                        stock_list: List[str] = [], 
                        field_list: List[str] = [], 
                        start_time: str = '', 
                        end_time: str = '') -> Dict:
        """获取股票交易数据"""
        # 自动初始化连接
        cls._auto_initialize()
        # 必填入参检查
        if not stock_list:
            cls.close()
            raise ValueError("必传参数缺失：stock_list不能为空，请提供合约代码列表")
        
        if not check_stock_code_format(stock_list):
            tq.close()
            raise ValueError(f"{stock_list}异常")

        if not end_time:
            end_time = datetime.now().strftime('%Y%m%d%H%M%S')

        # 格式化时间参数
        if start_time:
            start_time = _convert_time_format(start_time)
        if end_time:
            end_time = _convert_time_format(end_time)

        timeout_ms = 60000 # 60秒超时
        result_dict = {}    # 返回结果字典

        for stock in stock_list:
            try:
                stock_json = {  "id" : cls._get_run_id(),
                                "type": "3",
                                "code": stock,
                                "table_list": field_list,
                                "start_time": start_time,
                                "end_time": end_time}
                json_str = json.dumps(stock_json, ensure_ascii=False)
                json_str = json_str.encode('utf-8')
                ptr = dll.GetProDataInStr(cls._get_run_id(),json_str,timeout_ms)
                # 检查返回的指针
                if ptr is None or len(ptr) == 0:
                    print(f"获取{stock}股票交易数据失败: 返回空指针")
                    continue

                # 解析JSON数据
                try:
                    data_dict = json.loads(ptr)
                except json.JSONDecodeError as e:
                    print(f"获取{stock}股票交易数据失败: JSON解析错误 - {e}")
                    print(f"原始返回数据: {ptr}")
                    continue

                # 检查错误代码
                if data_dict.get("ErrorId") != "0":
                    print(f"获取{stock}股票交易数据错误: {data_dict.get('Error')}")
                    continue

                result_dict[stock] = data_dict['Data']

            except Exception as e:
                print(f"获取{stock}财务数据异常: {e}")
                import traceback
                traceback.print_exc()
                continue

        return result_dict
    
    @classmethod
    def get_gpjy_value_by_date(cls,
                                stock_list: List[str] = [], 
                                field_list: List[str] = [],  
                                year: int = 0,
                                mmdd: int = 0) -> Dict:
        """获取股票交易数据"""
        # 自动初始化连接
        cls._auto_initialize()
        # 必填入参检查
        if not stock_list:
            cls.close()
            raise ValueError("必传参数缺失：stock_list不能为空，请提供合约代码列表")
        
        if not check_stock_code_format(stock_list):
            tq.close()
            raise ValueError(f"{stock_list}异常")

        timeout_ms = 60000 # 60秒超时
        result_dict = {}    # 返回结果字典

        for stock in stock_list:
            try:
                stock_json = {  "id" : cls._get_run_id(),
                                "type": "4",
                                "code": stock,
                                "table_list": field_list,
                                "year": year,
                                "mmdd": mmdd}
                json_str = json.dumps(stock_json, ensure_ascii=False)
                json_str = json_str.encode('utf-8')
                ptr = dll.GetProDataInStr(cls._get_run_id(),json_str,timeout_ms)
                # 检查返回的指针
                if ptr is None or len(ptr) == 0:
                    print(f"获取{stock}股票交易数据失败: 返回空指针")
                    continue

                # 解析JSON数据
                try:
                    data_dict = json.loads(ptr)
                except json.JSONDecodeError as e:
                    print(f"获取{stock}股票交易数据失败: JSON解析错误 - {e}")
                    print(f"原始返回数据: {ptr}")
                    continue

                # 检查错误代码
                if data_dict.get("ErrorId") != "0":
                    print(f"获取{stock}股票交易数据错误: {data_dict.get('Error')}")
                    continue

                result_dict[stock] = data_dict['Data']

            except Exception as e:
                print(f"获取{stock}财务数据异常: {e}")
                import traceback
                traceback.print_exc()
                continue

        return result_dict
    
    @classmethod
    def get_bkjy_value(cls,
                        stock_list: List[str] = [], 
                        field_list: List[str] = [], 
                        start_time: str = '', 
                        end_time: str = '') -> Dict:
        """获取板块交易数据"""
        # 自动初始化连接
        cls._auto_initialize()
        # 必填入参检查
        if not stock_list:
            cls.close()
            raise ValueError("必传参数缺失：stock_list不能为空，请提供合约代码列表")
        
        if not check_stock_code_format(stock_list):
            tq.close()
            raise ValueError(f"{stock_list}异常")

        if not end_time:
            end_time = datetime.now().strftime('%Y%m%d%H%M%S')

        # 格式化时间参数
        if start_time:
            start_time = _convert_time_format(start_time)
        if end_time:
            end_time = _convert_time_format(end_time)

        timeout_ms = 60000 # 60秒超时
        result_dict = {}    # 返回结果字典

        for stock in stock_list:
            try:
                stock_json = {  "id" : cls._get_run_id(),
                                "type": "5",
                                "code": stock,
                                "table_list": field_list,
                                "start_time": start_time,
                                "end_time": end_time}
                json_str = json.dumps(stock_json, ensure_ascii=False)
                json_str = json_str.encode('utf-8')
                ptr = dll.GetProDataInStr(cls._get_run_id(),json_str,timeout_ms)
                # 检查返回的指针
                if ptr is None or len(ptr) == 0:
                    print(f"获取{stock}股票交易数据失败: 返回空指针")
                    continue

                # 解析JSON数据
                try:
                    data_dict = json.loads(ptr)
                except json.JSONDecodeError as e:
                    print(f"获取{stock}股票交易数据失败: JSON解析错误 - {e}")
                    print(f"原始返回数据: {ptr}")
                    continue

                # 检查错误代码
                if data_dict.get("ErrorId") != "0":
                    print(f"获取{stock}股票交易数据错误: {data_dict.get('Error')}")
                    continue

                result_dict[stock] = data_dict['Data']

            except Exception as e:
                print(f"获取{stock}财务数据异常: {e}")
                import traceback
                traceback.print_exc()
                continue

        return result_dict
    
    @classmethod
    def get_bkjy_value_by_date(cls,
                                stock_list: List[str] = [], 
                                field_list: List[str] = [],  
                                year: int = 0,
                                mmdd: int = 0) -> Dict:
        """获取板块交易数据"""
        # 自动初始化连接
        cls._auto_initialize()
        # 必填入参检查
        if not stock_list:
            cls.close()
            raise ValueError("必传参数缺失：stock_list不能为空，请提供合约代码列表")
        
        if not check_stock_code_format(stock_list):
            tq.close()
            raise ValueError(f"{stock_list}异常")

        timeout_ms = 60000 # 60秒超时
        result_dict = {}    # 返回结果字典

        for stock in stock_list:
            try:
                stock_json = {  "id" : cls._get_run_id(),
                                "type": "6",
                                "code": stock,
                                "table_list": field_list,
                                "year": year,
                                "mmdd": mmdd}
                json_str = json.dumps(stock_json, ensure_ascii=False)
                json_str = json_str.encode('utf-8')
                ptr = dll.GetProDataInStr(cls._get_run_id(),json_str,timeout_ms)
                # 检查返回的指针
                if ptr is None or len(ptr) == 0:
                    print(f"获取{stock}股票交易数据失败: 返回空指针")
                    continue

                # 解析JSON数据
                try:
                    data_dict = json.loads(ptr)
                except json.JSONDecodeError as e:
                    print(f"获取{stock}股票交易数据失败: JSON解析错误 - {e}")
                    print(f"原始返回数据: {ptr}")
                    continue

                # 检查错误代码
                if data_dict.get("ErrorId") != "0":
                    print(f"获取{stock}股票交易数据错误: {data_dict.get('Error')}")
                    continue

                result_dict[stock] = data_dict['Data']

            except Exception as e:
                print(f"获取{stock}财务数据异常: {e}")
                import traceback
                traceback.print_exc()
                continue

        return result_dict

    @classmethod
    def get_scjy_value(cls,
                        field_list: List[str] = [], 
                        start_time: str = '', 
                        end_time: str = '') -> Dict:
        """获取市场交易数据"""
        # 自动初始化连接
        cls._auto_initialize()

        if not end_time:
            end_time = datetime.now().strftime('%Y%m%d%H%M%S')

        # 格式化时间参数
        if start_time:
            start_time = _convert_time_format(start_time)
        if end_time:
            end_time = _convert_time_format(end_time)

        timeout_ms = 60000 # 60秒超时
        try:
            stock_json = {  "id" : cls._get_run_id(),
                            "type": "7",
                            "code": "999999.SH",
                            "table_list": field_list,
                            "start_time": start_time,
                            "end_time": end_time}
            json_str = json.dumps(stock_json, ensure_ascii=False)
            json_str = json_str.encode('utf-8')
            ptr = dll.GetProDataInStr(cls._get_run_id(),json_str,timeout_ms)
            # 检查返回的指针
            if ptr is None or len(ptr) == 0:
                tq.close()
                raise ValueError(f"获取市场交易数据失败: 返回空指针")
                
            # 解析JSON数据
            try:
                data_dict = json.loads(ptr)
            except json.JSONDecodeError as e:
                tq.close()
                print(f"获取市场交易数据失败: JSON解析错误 - {e}")
                raise ValueError(f"原始返回数据: {ptr}")

            # 检查错误代码
            if data_dict.get("ErrorId") != "0":
                tq.close()
                raise ValueError(f"获取市场交易数据错误: {data_dict.get('Error')}")

        except Exception as e:
            tq.close()
            print(f"获取市场交易数据异常: {e}")
            import traceback
            traceback.print_exc()
        return data_dict['Data']
    
    @classmethod
    def get_scjy_value_by_date(cls,
                                field_list: List[str] = [],  
                                year: int = 0,
                                mmdd: int = 0) -> Dict:
        """获取市场交易数据"""
        # 自动初始化连接
        cls._auto_initialize()

        timeout_ms = 60000 # 60秒超时
        try:
            stock_json = {  "id" : cls._get_run_id(),
                            "type": "8",
                            "code": "999999.SH",
                            "table_list": field_list,
                            "year": year,
                            "mmdd": mmdd}
            json_str = json.dumps(stock_json, ensure_ascii=False)
            json_str = json_str.encode('utf-8')
            ptr = dll.GetProDataInStr(cls._get_run_id(),json_str,timeout_ms)
            # 检查返回的指针
            if ptr is None or len(ptr) == 0:
                tq.close()
                raise ValueError(f"获取市场交易数据失败: 返回空指针")
                
            # 解析JSON数据
            try:
                data_dict = json.loads(ptr)
            except json.JSONDecodeError as e:
                tq.close()
                print(f"获取市场交易数据失败: JSON解析错误 - {e}")
                raise ValueError(f"原始返回数据: {ptr}")

            # 检查错误代码
            if data_dict.get("ErrorId") != "0":
                tq.close()
                raise ValueError(f"获取市场交易数据错误: {data_dict.get('Error')}")

        except Exception as e:
            tq.close()
            print(f"获取市场交易数据异常: {e}")
            import traceback
            traceback.print_exc()
        return data_dict['Data']
    
    @classmethod
    def get_gp_one_data(cls,
                        stock_list: List[str] = [], 
                        field_list: List[str] = []) -> Dict:
        """获取股票单个数据"""
        # 自动初始化连接
        cls._auto_initialize()
        # 必填入参检查
        if not stock_list:
            cls.close()
            raise ValueError("必传参数缺失：stock_list不能为空，请提供合约代码列表")
        
        if not check_stock_code_format(stock_list):
            tq.close()
            raise ValueError(f"{stock_list}异常")

        timeout_ms = 60000 # 60秒超时
        result_dict = {}    # 返回结果字典

        for stock in stock_list:
            try:
                stock_json = {  "id" : cls._get_run_id(),
                                "type": "9",
                                "code": stock,
                                "table_list": field_list}
                json_str = json.dumps(stock_json, ensure_ascii=False)
                json_str = json_str.encode('utf-8')
                ptr = dll.GetProDataInStr(cls._get_run_id(),json_str,timeout_ms)
                # 检查返回的指针
                if ptr is None or len(ptr) == 0:
                    print(f"获取{stock}股票交易数据失败: 返回空指针")
                    continue

                # 解析JSON数据
                try:
                    data_dict = json.loads(ptr)
                except json.JSONDecodeError as e:
                    print(f"获取{stock}股票交易数据失败: JSON解析错误 - {e}")
                    print(f"原始返回数据: {ptr}")
                    continue

                # 检查错误代码
                if data_dict.get("ErrorId") != "0":
                    print(f"获取{stock}股票交易数据错误: {data_dict.get('Error')}")
                    continue

                result_dict[stock] = data_dict['Data']

            except Exception as e:
                print(f"获取{stock}财务数据异常: {e}")
                import traceback
                traceback.print_exc()
                continue

        return result_dict
    
    @classmethod
    def get_trading_calendar(cls,
                            market: str,
                            start_time: str,
                            end_time: str) -> List:
        """获取交易日历"""
        # 自动初始化连接
        cls._auto_initialize()
        
        # 格式化时间参数
        if start_time:
            start_time = _convert_time_format(start_time)
        if end_time:
            end_time = _convert_time_format(end_time)

        marketstr = market.encode('utf-8')
        startimestr = start_time.encode('utf-8')
        endtimestr = end_time.encode('utf-8')
        timeout_ms = 5000
        try:
            ptr = dll.GetTradeCalendarInStr(cls._get_run_id(), marketstr, startimestr, endtimestr, -1, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("获取交易日历失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"获取交易日历错误: {json_res.get('Error')}")
            return json_res.get("Date", [])
        except Exception as e:
            cls.close()
            raise ValueError("获取交易日历异常")
        
    @classmethod
    def get_trading_dates(cls,
                            market: str,
                            start_time: str,
                            end_time: str,
                            count:int = -1) -> List:
        """获取交易日列表"""
        # 自动初始化连接
        cls._auto_initialize()
        
        # 格式化时间参数
        if start_time:
            start_time = _convert_time_format(start_time)
        if end_time:
            end_time = _convert_time_format(end_time)

        marketstr = market.encode('utf-8')
        startimestr = start_time.encode('utf-8')
        endtimestr = end_time.encode('utf-8')
        timeout_ms = 5000
        try:
            ptr = dll.GetTradeCalendarInStr(cls._get_run_id(), marketstr, startimestr, endtimestr, count, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("获取交易日历失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"获取交易日历错误: {json_res.get('Error')}")
            return json_res.get("Date", [])
        except Exception as e:
            cls.close()
            raise ValueError("获取交易日历异常")

    @classmethod
    def get_stock_list(cls,
                       market = None) -> List:
        """获取股票列表"""
        # 自动初始化连接
        cls._auto_initialize()

        if not market:
            market = '5'
        marketstr = market.encode('utf-8')
        timeout_ms = 5000

        try:
            ptr = dll.GetStockListInStr(cls._get_run_id(), marketstr, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("获取股票列表失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"获取股票列表错误: {json_res.get('Error')}")
            result = [item.replace('.1', '.SH').replace('.0', '.SZ').replace('.2', '.BJ') for item in json_res['Value']]
            return result
        except Exception as e:
            cls.close()
            raise ValueError("获取股票列表异常")
        

    @classmethod
    def order_stock(cls,
                    account:str, 
                    stock_code:str, 
                    order_type:int, 
                    order_volume:int, 
                    price_type:int, 
                    price:float, 
                    strategy_name:str, 
                    order_remark: str = ''):
        """下单接口 暂无实际功能"""
        # 自动初始化连接
        cls._auto_initialize()

        # 必填入参检查
        if not account:
            cls.close()
            raise ValueError("必传参数缺失：account不能为空，请提供账户信息")
        if not stock_code:
            cls.close()
            raise ValueError("必传参数缺失：stock_code不能为空，请提供合约代码")
        
        if not check_stock_code_format(stock_code):
            tq.close()
            raise ValueError(f"{stock_code}异常")

        try:
            account_str = account.encode('utf-8') 
            code = stock_code.encode('utf-8')
            if order_remark is not None:
                remark = order_remark.encode('utf-8')

            timeout_ms = 5000
            ptr = dll.SetNewOrder(cls._get_run_id(), account_str, code, order_type, order_volume,
                                price_type, price, remark, timeout_ms)

            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
                data_json = json.loads(result_str)
                if data_json.get("ErrorId") != "0":
                    print(f"下单{stock_code}数据错误: {data_json}")
                    return -1;
                return data_json
            return -1
        except Exception as e:
            print(f"下单{stock_code}数据异常: {e}")
            import traceback
            traceback.print_exc()
            return -1

    @classmethod
    def subscribe_quote(cls, 
                        stock_code: str, 
                        period: str = '1d', 
                        start_time: str = '', 
                        end_time: str = '', 
                        count: int = 0, 
                        dividend_type: Optional[str] = None,  # 改为Optional类型
                        callback = None):
        """订阅单股行情数据回调 暂无实际功能"""
        # 自动初始化连接
        cls._auto_initialize()
        # 必填入参检查
        if not stock_code:
            cls.close()
            raise ValueError("必传参数缺失：stock_code不能为空，请提供合约代码")
        if not period:
            cls.close()
            raise ValueError("必传参数缺失：period不能为空，请指定数据周期（如'1d','1m','tick'等）")
        
        if not check_stock_code_format(stock_code):
            tq.close()
            raise ValueError(f"{stock_code}异常")

        # 时间参数检查：count<0时必须提供起始和结束时间
        if count < 0:
            if not start_time:
                cls.close()
                raise ValueError("必传参数缺失：start_time不能为空，当count<0时必须指定起始时间")
            if not end_time:
                cls.close()
                raise ValueError("必传参数缺失：end_time不能为空，当count<0时必须指定结束时间")

        # 转换时间格式
        if start_time:
            start_time = _convert_time_format(start_time)
        if end_time:
            end_time = _convert_time_format(end_time)

         # 如果未传入dividend_type，默认为'none'
        if dividend_type is None:
            dividend_type = 'none'

        # 转换除权类型
        dividend_type_map = {
            'none': 0,  # 不复权（默认）
            'front': 1,  # 前复权
            'back': 2  # 后复权
        }
        # 统一转为小写处理，增强容错性
        dividend_type_int = dividend_type_map.get(dividend_type.lower(), 0)

        # 判断回调函数是否合法
        if callback is None:
            cls.close()
            raise ValueError("回调函数不能为空，请提供有效的回调函数")

        # 注册外套回调函数
        if cls.m_is_init_data_transfer == False:
            CALLBACK_FUNC_TYPE = ctypes.CFUNCTYPE(None, ctypes.c_char_p)
            cls.data_transfer = CALLBACK_FUNC_TYPE(cls._data_callback_transfer)
            dll.Register_DataTransferFunc(cls._get_run_id(), cls.data_transfer)
            cls.m_is_init_data_transfer = True

        codestr = stock_code.encode('utf-8')
        startimestr = start_time.encode('utf-8')
        endtimestr = end_time.encode('utf-8')
        periodstr = period.encode('utf-8')

        cls.data_callback_func[cls._get_run_id()][stock_code] = callback
        try:
            timeout_ms = 10000
            ptr = dll.SubscribeGPData(cls._get_run_id(), codestr, startimestr, endtimestr, periodstr, 
            dividend_type_int, count, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError(f"订阅{stock_code}失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"订阅{stock_code}失败: {json_res.get('Error')}")
            return result_str
        except Exception as e:
            cls.close()
            raise ValueError(f"订阅{stock_code}异常")
    
    @classmethod
    def subscribe_hq(cls, 
                     stock_list: List[str] = [], 
                     callback = None):
        """订阅单股行情更新"""
        # 自动初始化连接
        cls._auto_initialize()
        # 必填入参检查
        if not stock_list:
            cls.close()
            raise ValueError("必传参数缺失：stock_list不能为空，请提供合约代码")
        
        if not check_stock_code_format(stock_list):
            tq.close()
            raise ValueError(f"{stock_list}异常")
        
        _sub_hq_update = cls._sub_hq_update
        combined = list(set(cls._sub_hq_update) | set(stock_list))
        cls._sub_hq_update.clear()
        cls._sub_hq_update.extend(combined)
      
        if len( cls._sub_hq_update) > 100:
            cls._sub_hq_update = _sub_hq_update
            tq.close()
            raise ValueError("订阅数大于100")
        
        # 判断回调函数是否合法
        if is_callback_func(callback) == False:
            cls.close()
            raise ValueError("回调函数格式错误，请提供有效的回调函数")

        # 注册外套回调函数
        if cls.m_is_init_data_transfer == False:
            CALLBACK_FUNC_TYPE = ctypes.CFUNCTYPE(None, ctypes.c_char_p)
            cls.data_transfer = CALLBACK_FUNC_TYPE(cls._data_callback_transfer)
            dll.Register_DataTransferFunc(cls._get_run_id(), cls.data_transfer)
            cls.m_is_init_data_transfer = True

        codestr = ','.join(stock_list)
        codestr = codestr.encode('utf-8')
        try:
            timeout_ms = 10000
            ptr = dll.SubscribeHQDUpdate(cls._get_run_id(), codestr, 0, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError(f"订阅{stock_list}失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"订阅{stock_list}失败: {json_res.get('Error')}")
            # 保存回调函数
            for stock in stock_list:
                cls.data_callback_func[cls._get_run_id()][stock] = callback
            return result_str
        except Exception as e:
            cls.close()
            raise ValueError(f"订阅{stock_list}异常")

    @classmethod
    def unsubscribe_hq(cls, 
                     stock_list: List[str] = []):
        """订阅单股行情更新"""
        # 自动初始化连接
        cls._auto_initialize()
        # 必填入参检查
        if not stock_list:
            cls.close()
            raise ValueError("必传参数缺失：stock_list不能为空，请提供合约代码")
        
        if not check_stock_code_format(stock_list):
            tq.close()
            raise ValueError(f"{stock_list}异常")
        
        a_set = set(cls._sub_hq_update)
        b_set = set(stock_list)
        _sub_hq_update = cls._sub_hq_update
        cls._sub_hq_update.clear()
        cls._sub_hq_update.extend(a_set - b_set)

        if len( cls._sub_hq_update) > 100:
            cls._sub_hq_update = _sub_hq_update
            tq.close()
            raise ValueError("订阅数大于100")

        
        codestr = ','.join(stock_list)
        codestr = codestr.encode('utf-8')
        try:
            timeout_ms = 10000
            ptr = dll.SubscribeHQDUpdate(cls._get_run_id(), codestr, 1, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError(f"取消订阅{stock_list}失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"取消订阅{stock_list}失败: {json_res.get('Error')}")
            
            #去掉对应保存的回调函数
            for run_id in list(cls.data_callback_func.keys()):  # 用list()避免遍历中修改字典导致的异常
                stock_dict = cls.data_callback_func[run_id]
                # 遍历需要删除的stock，若存在则删除
                for stock in b_set:
                    if stock in stock_dict:
                        del stock_dict[stock]
            return result_str
        except Exception as e:
            cls.close()
            raise ValueError(f"取消订阅{stock_list}异常")
        
    @classmethod
    def get_subscribe_hq_stock_list(cls):
        return cls._sub_hq_update

    @classmethod
    def refresh_cache(cls):
        """刷新缓存行情"""
        # 自动初始化连接
        cls._auto_initialize()
        try:
            timeout_ms = 100000
            ptr = dll.ReFreshCacheAll(cls._get_run_id(), timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("刷新缓存行情失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"刷新缓存行情失败: {json_res.get('Error')}")
            return result_str
        except Exception as e:
            cls.close()
            raise ValueError("刷新缓存行情异常")
        
    @classmethod
    def refresh_kline(cls,
                      stock_list: List[str] = [],
                      period: str = ''):
        """刷新K线缓存"""
        if not check_stock_code_format(stock_list):
            tq.close()
            raise ValueError(f"{stock_list}异常")
        cls._auto_initialize()

        # 周期校验
        valid_periods = ['1m', '5m', '1d']
        if period.lower() not in valid_periods:
            tq.close()
            raise ValueError(f'不支持{period},仅支持{valid_periods}')

        code_str = ','.join(stock_list)
        code_str = code_str.encode('utf-8')
        period_str = period.encode('utf-8')
        try:
            timeout_ms = 1000000
            ptr = dll.ReFreshCacheKLine(cls._get_run_id(), code_str, period_str, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("刷新数据缓存失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"刷新K线缓存失败: {json_res.get('Error')}")
            return result_str
        except Exception as e:
            cls.close()
            raise ValueError("刷新数据缓存异常")
        
    @classmethod
    def download_file(cls,
                      stock_code: str = '',
                      down_time:str = '',
                      down_type:int = 1):
        """下载文件（10大股东，ETF申赎数据等）"""
        cls._auto_initialize()

        if not stock_code:
            cls.close()
            raise ValueError("证券代码不能未空")
        if not down_time:
            cls.close()
            raise ValueError("下载日期不能为空")
        
        down_time = _convert_time_format(down_time)
        
        code_str = stock_code.encode('utf-8')
        time_str = down_time.encode('utf-8')
        try:
            timeout_ms = 1000000
            ptr = dll.DownLoadFiles(cls._get_run_id(), code_str, time_str, down_type, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("下载文件失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"下载文件失败: {json_res.get('Error')}")
            return result_str
        except Exception as e:
            cls.close()
            raise ValueError("下载文件异常")
        
    @classmethod
    def create_sector(cls,
                      block_code:str = '',
                      block_name:str = ''):
        '''创建自定义板块'''
        cls._auto_initialize()

        if not block_code:
            cls.close()
            raise ValueError("板块简称不能未空")
        if not block_name:
            cls.close()
            raise ValueError("板块名称不能为空")

        code_str = block_code.encode('utf-8')
        name_str = block_name.encode('utf-8')
        try:
            timeout_ms = 10000
            ptr = dll.UserBlockControl(cls._get_run_id(), 1, code_str, name_str, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("创建板块失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"创建板块失败: {json_res.get('Error')}")
            return result_str
        except Exception as e:
            cls.close()
            raise ValueError("创建板块异常")
        
    @classmethod
    def delete_sector(cls,
                      block_code:str = ''):
        '''删除自定义板块'''
        cls._auto_initialize()

        if not block_code:
            cls.close()
            raise ValueError("板块简称不能未空")
        code_str = block_code.encode('utf-8')
        name_str = 'none'.encode('utf-8')
        try:
            timeout_ms = 10000
            ptr = dll.UserBlockControl(cls._get_run_id(), 2, code_str, name_str, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("删除板块失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"删除板块失败: {json_res.get('Error')}")
            return result_str
        except Exception as e:
            cls.close()
            raise ValueError("删除板块异常")
        
    @classmethod
    def rename_sector(cls,
                      block_code:str = '',
                      block_name:str = ''):
        '''重命名自定义板块'''
        cls._auto_initialize()

        if not block_code:
            cls.close()
            raise ValueError("板块简称不能未空")
        if not block_name:
            cls.close()
            raise ValueError("板块名称不能为空")

        code_str = block_code.encode('utf-8')
        name_str = block_name.encode('utf-8')
        try:
            timeout_ms = 10000
            ptr = dll.UserBlockControl(cls._get_run_id(), 3, code_str, name_str, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("重命名板块失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"重命名板块失败: {json_res.get('Error')}")
            return result_str
        except Exception as e:
            cls.close()
            raise ValueError("重命名板块异常")
        
    @classmethod
    def clear_sector(cls,
                      block_code:str = ''):
        '''清空自定义板块'''
        cls._auto_initialize()

        if not block_code:
            cls.close()
            raise ValueError("板块简称不能未空")
        
        code_str = block_code.encode('utf-8')
        name_str = 'none'.encode('utf-8')
        try:
            timeout_ms = 10000
            ptr = dll.UserBlockControl(cls._get_run_id(), 4, code_str, name_str, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("清空板块失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                cls.close()
                raise ValueError(f"清空板块失败: {json_res.get('Error')}")
            return result_str
        except Exception as e:
            cls.close()
            raise ValueError("清空板块异常")

    @classmethod
    def get_cb_info(cls,
                    stock_code:str = ''):
        '''获取可转债基础信息'''
        cls._auto_initialize()

        if not stock_code:
            cls.close()
            raise ValueError("可转债代码不能为空")

        code_str = stock_code.encode('utf-8')
        try:
            timeout_ms = 10000
            ptr = dll.GetCBINFOInStr(cls._get_run_id(), code_str, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("获取可转债信息失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                print(f"获取可转债信息失败: {json_res.get('Error')}")
                return {}
            return json_res["Data"][0]
        except Exception as e:
            cls.close()
            raise ValueError("获取可转债信息异常")
        
    @classmethod
    def get_ipo_info(cls,
                    ipo_type:int = 0,
                    ipo_date:int = 0):
        '''获取新股申购信息'''
        cls._auto_initialize()
        try:
            timeout_ms = 10000
            ptr = dll.GetIPOINFOInStr(cls._get_run_id(), ipo_type, ipo_date, timeout_ms)
            if len(ptr) > 0:
                result_str = ptr.decode('utf-8')
            else:
                cls.close()
                raise ValueError("获取新股申购信息失败: 返回空指针")
            json_res = json.loads(result_str)
            if json_res.get("ErrorId") != "0":
                print(f"获取新股申购信息失败: {json_res.get('Error')}")
                return []
            return json_res["Data"]
        except Exception as e:
            cls.close()
            raise ValueError("获取新股申购信息异常")
        


