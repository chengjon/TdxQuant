import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import vectorbt as vbt
from sklearn.linear_model import LinearRegression
from typing import Union
from tqcenter import tdxdata  # 导入tdxdata，内部获取基准数据

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class evaluation:
    """支持内部获取基准数据的VBT评价工具（入参：基准代码、回测起止时间等）"""
    def __init__(
            self,
            vbt_portfolio: vbt.Portfolio,
            benchmark_code: str,  # 基准代码（如'000300.SH'）
            start_time: str,      # 回测开始时间（如'2025-06-01'）
            end_time: str,        # 回测结束时间（如'2025-10-01'）
            annualization_factor_full: int = 252,
            # 可选：tdxdata.get_market_data的其他参数
            period: str = '1d'
    ):
        # 1. 初始化基础参数
        self.pf = vbt_portfolio
        self.benchmark_code = benchmark_code
        self.start_time = start_time
        self.end_time = end_time
        self.annualization_factor_full = annualization_factor_full

        # 2. 内部调用get_market_data获取基准数据
        self.benchmark_close = self._fetch_benchmark_data(
            dividend_type='none',
            period=period
        )

        # 3. 提取策略数据并对齐时间轴
        self.strategy_equity = self._get_strategy_equity()
        self.strategy_returns = self.strategy_equity.pct_change().dropna()
        self._align_time_axis_strict()  # 严格对齐策略与基准的时间

        # 4. 计算基准相关指标
        self.benchmark_equity = self._get_benchmark_equity()
        self.benchmark_returns = self.benchmark_equity.pct_change().dropna()
        self.excess_returns = self._calculate_excess_returns()

        # 5. 计算回测周期参数
        self.actual_trading_days = len(self.strategy_equity)
        self.backtest_duration_days = (self.strategy_equity.index[-1] - self.strategy_equity.index[0]).days

        # 6. 预计算所有指标并校验
        self.metrics = self._calculate_all_metrics()
        self._validate_return_consistency()

    def _fetch_benchmark_data(self, dividend_type: str, period: str) -> pd.Series:
        """内部调用tdxdata获取基准收盘价，返回Series"""
        # 调用get_market_data获取基准数据（返回字典）
        benchmark_start_time = (pd.to_datetime(self.start_time) - pd.Timedelta(days=1)).strftime('%Y%m%d')

        df_benchmark = tdxdata.get_market_data(
            field_list=['Close'],
            stock_list=[self.benchmark_code],
            start_time=benchmark_start_time,
            end_time=self.end_time,
            dividend_type=dividend_type,
            period=period,
            fill_data=True  # 自动填充缺失值（根据tdxdata特性调整）
        )

        # 转换为Series（确保只有一列收盘价）
        benchmark_series = tdxdata.price_df(df_benchmark, 'Close')
        benchmark_series.index = pd.to_datetime(benchmark_series.index)  # 标准化索引为datetime

        return benchmark_series

    def _format_series(self, data: Union[pd.Series, pd.DataFrame, np.ndarray]) -> pd.Series:
        """兼容多种输入格式（内部调用，处理基准数据）"""
        if isinstance(data, pd.DataFrame):
            if data.shape[1] != 1:
                raise ValueError(f"基准数据为DataFrame时必须只有1列，当前有{data.shape[1]}列")
            series_data = data.iloc[:, 0]
            return series_data
        elif isinstance(data, pd.Series):
            data.index = pd.to_datetime(data.index)
            return data.sort_index()
        else:
            raise TypeError("基准数据必须是 pd.Series、pd.DataFrame 或 np.ndarray 类型")

    def _get_strategy_equity(self) -> pd.Series:
        """获取策略总资产净值（单变量，而非多资产分别的净值）"""
        # 若portfolio是多资产组合，取总价值而非单个资产价值
        total_equity = self.pf.value()  # 多列求和→单变量
        unit_equity = total_equity / total_equity.iloc[0]  # 归一化（初始值=1）
        unit_equity.name = "Strategy"

        return unit_equity

    def _align_time_axis_strict(self) -> None:
        """严格对齐策略与基准的时间轴（仅保留共同交易日）"""
        strategy_dates = self.strategy_equity.index
        # 检查基准数据是否包含所有策略交易日
        missing_dates = strategy_dates[~strategy_dates.isin(self.benchmark_close.index)]
        if len(missing_dates) > 0:
            raise ValueError(
                f"基准数据缺少{len(missing_dates)}个策略交易日的数据，示例缺失日期：{missing_dates[:5].tolist()}"
            )
        # 截取一致的时间范围
        self.benchmark_close = self.benchmark_close.loc[strategy_dates]
        self.strategy_equity = self.strategy_equity.loc[strategy_dates]

    def _get_benchmark_equity(self) -> pd.Series:
        """计算基准净值（归一化，确保单值 Series）"""
        unit_equity = self.benchmark_close / self.benchmark_close.iloc[0]
        # 若基准净值是多列，强制取第一列并转为单值 Series
        if isinstance(unit_equity, pd.DataFrame):
            unit_equity = unit_equity.iloc[:, 0].squeeze()  # 转为 Series
        return unit_equity

    def _calculate_excess_returns(self) -> pd.Series:
        """计算策略相对于基准的超额收益（确保单变量）"""
        common_dates = self.strategy_returns.index.intersection(self.benchmark_returns.index)

        # 强制将策略收益转为单变量（若为多列则聚合）
        if isinstance(self.benchmark_returns, pd.DataFrame):
            # 若只有一列，用squeeze()转为Series；若多列，取第一列
            self.benchmark_returns = self.benchmark_returns.squeeze(axis=1)
            print("基准收益已从DataFrame转为Series")

        # 确认策略收益是Series（若不是则转换）
        if isinstance(self.strategy_returns, pd.DataFrame):
            self.strategy_returns = self.strategy_returns.squeeze(axis=1)

        # 计算超额收益
        excess = self.strategy_returns.loc[common_dates] - self.benchmark_returns.loc[common_dates]
        excess.name = "Excess Returns"

        # 最终检查，若仍为多列则报错
        if isinstance(excess, pd.DataFrame):
            if excess.shape[1] == 1:
                excess = excess.squeeze()  # 转为Series
            else:
                raise ValueError("超额收益计算结果应为单变量，却得到多列数据")
        return excess

    def _calculate_all_metrics(self) -> dict:
        """计算所有评价指标（含年化收益、风险、Alpha/Beta等）"""
        # 总收益（强制提取标量）
        strategy_total = (self.strategy_equity.iloc[-1] - 1) * 100
        # 基准总收益：若为Series，取最后一个元素的标量值
        benchmark_total_raw = (self.benchmark_equity.iloc[-1] - 1) * 100
        benchmark_total = benchmark_total_raw.item() if isinstance(benchmark_total_raw,
              (pd.Series, pd.DataFrame)) else benchmark_total_raw

        # 年化因子（动态计算）
        if self.backtest_duration_days == 0:
            raise ValueError("回测周期长度为0，请检查时间范围")
        annual_factor = self.annualization_factor_full / self.actual_trading_days

        # 年化收益（强制提取标量）
        strategy_annual = ((1 + strategy_total / 100) ** annual_factor - 1) * 100
        # 基准年化收益：确保是标量
        benchmark_annual_raw = ((1 + benchmark_total / 100) ** annual_factor - 1) * 100
        benchmark_annual = benchmark_annual_raw.item() if isinstance(benchmark_annual_raw, (
        pd.Series, pd.DataFrame)) else benchmark_annual_raw

        # 超额收益（年化）- 确保是标量
        excess_total = strategy_total - benchmark_total
        excess_annual = ((1 + excess_total / 100) ** annual_factor - 1) * 100
        # 若excess_annual是Series，取其值（单元素Series转换为标量）
        if isinstance(excess_annual, pd.Series):
            excess_annual = excess_annual.item()

        # 超额收益胜率
        excess_win_rate = (self.excess_returns > 0).mean() * 100

        # 波动率（年化）- 确保是标量
        strategy_vol = self.strategy_returns.std().item() * np.sqrt(annual_factor) * 100
        benchmark_vol = self.benchmark_returns.std().item() * np.sqrt(annual_factor) * 100
        excess_vol = self.excess_returns.std().item() * np.sqrt(annual_factor) * 100  # 已用.item()确保标量

        # 补充：计算Alpha和Beta（核心新增部分）
        # 确保策略收益和基准收益的时间对齐
        common_returns_dates = self.strategy_returns.index.intersection(self.benchmark_returns.index)
        X = self.benchmark_returns.loc[common_returns_dates].values.reshape(-1, 1)  # 基准收益作为自变量
        y = self.strategy_returns.loc[common_returns_dates].values  # 策略收益作为因变量

        # 拟合线性回归模型
        lr = LinearRegression(fit_intercept=True)  # 必须保留截距项（Alpha的来源）
        lr.fit(X, y)

        # 提取Beta（斜率）和Alpha（截距项，需年化）
        beta = lr.coef_[0]  # 斜率即Beta
        alpha_daily = lr.intercept_  # 日均Alpha（截距项）
        alpha_annual = alpha_daily * annual_factor * 100  # 年化Alpha（转为百分比）

        # 信息比率（确保分子分母都是标量）
        if excess_vol != 0:
            info_ratio = excess_annual / excess_vol
            # 若计算后仍为Series，强制转为标量
            if isinstance(info_ratio, pd.Series):
                info_ratio = info_ratio.item()
        else:
            info_ratio = np.nan

        # 信息比率判断（使用标量判断）
        info_ratio = round(info_ratio, 4) if not np.isnan(info_ratio) else "N/A"

        # 最大回撤（修复基准和相对回撤的标量提取）
        def max_drawdown(equity: pd.Series) -> float:
            rolling_max = equity.cummax()
            dd_series = ((equity - rolling_max) / rolling_max).min()
            # 从Series中提取标量值
            return dd_series.item() * 100 if isinstance(dd_series, (pd.Series, pd.DataFrame)) else dd_series * 100

        strategy_dd = max_drawdown(self.strategy_equity)
        benchmark_dd = max_drawdown(self.benchmark_equity)
        relative_dd = max_drawdown(self.strategy_equity / self.benchmark_equity)
        # 处理相对回撤可能的NaN（若全为NaN则设为0或提示）
        relative_dd = round(relative_dd, 2) if not np.isnan(relative_dd) else "N/A"



        return {
            "基准代码": self.benchmark_code,
            "回测时间范围": f"{self.start_time} ~ {self.end_time}",
            "实际交易日数": self.actual_trading_days,
            "年化因子": round(annual_factor, 2),
            "策略总收益率（%）": round(strategy_total, 2),
            "基准总收益率（%）": round(benchmark_total, 2),
            "策略年化收益率（%）": round(strategy_annual, 2),
            "基准年化收益率（%）": round(benchmark_annual, 2),
            "年化超额收益率（%）": round(excess_annual, 2),
            "策略年化波动率（%）": round(strategy_vol, 2),
            "基准年化波动率（%）": round(benchmark_vol, 2),
            "超额收益年化波动率（%）": round(excess_vol, 2),
            "Alpha（年化，%）": round(alpha_annual, 4),
            "Beta": round(beta, 4),
            "信息比率（IR）": round(info_ratio, 4) if not np.isnan(info_ratio) else "N/A",
            "策略最大回撤（%）": round(strategy_dd, 2),
            "基准最大回撤（%）": round(benchmark_dd, 2),
            "相对最大回撤（%）": round(relative_dd, 2),
            "超额收益胜率（%）": round(excess_win_rate, 2)
        }

    def _validate_return_consistency(self) -> None:
        """校验收益一致性（总收益与年化收益符号）"""
        # 从metrics中提取标量值（关键修复）
        benchmark_total = self.metrics["基准总收益率（%）"]
        benchmark_annual = self.metrics["基准年化收益率（%）"]

        # 确保是标量（若为Series则取其值）
        if isinstance(benchmark_total, pd.Series):
            benchmark_total = benchmark_total.item()
        if isinstance(benchmark_annual, pd.Series):
            benchmark_annual = benchmark_annual.item()

        # 进行判断
        if (benchmark_total > 0.1 and benchmark_annual < -0.1) or (benchmark_total < -0.1 and benchmark_annual > 0.1):
            print(f"⚠️ 警告：基准总收益（{benchmark_total:.2f}%）与年化收益（{benchmark_annual:.2f}%）符号相反")
        else:
            print(f"✅ 基准收益一致性校验通过")

    def show_metrics(self) -> None:
        """显示所有评价指标"""
        print("=" * 80)
        print(f"策略评价报告（基准：{self.benchmark_code}）")
        print("=" * 80)
        for key, value in self.metrics.items():
            print(f"{key:<20}: {value}")
        print("=" * 80)

    def plot_equity_curve(self, figsize: tuple = (12, 6)) -> None:
        """绘制策略与基准的净值对比图"""
        fig, ax = plt.subplots(figsize=figsize)
        self.strategy_equity.plot(ax=ax, linewidth=2, label=f"策略（年化：{self.metrics['策略年化收益率（%）']}%）")
        self.benchmark_equity.plot(ax=ax, linewidth=2, linestyle="--",
                                   label=f"（年化：{self.metrics['基准年化收益率（%）']}%）")
        ax.set_title(f"策略 vs {self.benchmark_code} 净值对比", fontsize=14)
        ax.set_xlabel("日期")
        ax.set_ylabel("单位净值（初始=1）")
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    def plot_excess_returns(self, figsize: tuple = (12, 4)) -> None:
        """绘制超额收益时序图"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)
        self.excess_returns.plot(ax=ax1, color="green", alpha=0.6, label="超额日收益")
        ax1.axhline(0, color="black", alpha=0.5)
        ax1.set_title(f"相对于{self.benchmark_code}的超额日收益")
        ax1.legend()

        (1 + self.excess_returns).cumprod().plot(ax=ax2, color="blue", label="累计超额收益")
        ax2.axhline(1, color="black", alpha=0.5)
        ax2.set_title("累计超额收益（初始=1）")
        ax2.set_xlabel("日期")
        ax2.legend()
        plt.tight_layout()
        plt.show()

    def get_metrics_df(self) -> pd.DataFrame:
        """返回指标DataFrame"""
        return pd.DataFrame([self.metrics]).T.rename(columns={0: "指标值"})
    
