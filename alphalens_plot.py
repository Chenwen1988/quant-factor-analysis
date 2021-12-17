#  -*- coding: utf-8 -*-

"""
This tutorial is modified based on the example from https://zhuanlan.zhihu.com/p/68613067
"""

__auth__ = 'Chen Chen, Yaxin Deng'

import pickle
import copy
import alphalens4m
import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
from helper import *
import time


# plt.style.use('ggplot')
plt.style.use('seaborn-pastel')

__PATH_FILE = os.path.dirname(__file__)
_ConfigFolder = 'Config'
_ConfigFile = 'config.json'
_InputFolder = 'Input'
_OutputFolder = 'Output'
_SubFolder = 'patent_invention_utility_count_session'
_Script = os.path.basename(__file__).rstrip('.py')
config = get_config(__PATH_FILE, _ConfigFolder, _ConfigFile)

pro = ts.pro_api(token=config.get('token'))    # , timeout=config.get('timeout')


@func_timer
def get_stock_code():
    df = pro.stock_basic(list_status='L')
    today = datetime.datetime.today()
    today_1year_ago = today - datetime.timedelta(days=365)
    # kick off new stock
    df = df[pd.to_datetime(df['list_date']) < today_1year_ago]
    # kick off st stocks
    df = df[-df['name'].apply(lambda x: x.startswith('*ST') or x.startswith('ST'))]
    stock_codes = df.ts_code.values.tolist()

    return stock_codes


@func_timer
def get_daily_basic():
    _codes = get_stock_code()
    _df_basic = pd.DataFrame()
    for code in _codes:
        print(code, _codes.index(code), len(_codes))
        df = pro.daily_basic(ts_code=code, start_date=config.get('start_date'), end_date=config.get('end_date'))
        _df_basic = pd.concat([_df_basic, df])
        time.sleep(0.3)  # 每分钟最多访问该接口200次
    print('Got daily data!')

    return _df_basic


@func_timer
def get_bar_data():
    _codes = get_stock_code()
    _df_bar = pd.DataFrame()
    for code in _codes:
        _df = pro.daily(ts_code=code, start_date=config.get('start_date'), end_date=config.get('end_date'))
        _df_bar = pd.concat([_df_bar, _df])
    print('Got bar data!')

    return _df_bar


@func_timer
def write_pickle_data(pickle_name, data_type, is_run=False):
    # pickle encounter memory error when data size is too big
    if not is_run:
        return
    if data_type == 'basic':
        df = get_daily_basic()
    elif data_type == 'bar':
        df = get_bar_data()
    else:
        print('Wrong data_type input...')
        return
    df.to_csv(f'{pickle_name}.csv')
    print("Saved",data_type,'data!')
    # with open(f'{pickle_name}.pkl', 'wb') as f:
    #     joblib.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)


@func_timer
def read_pickle_data(pickle_name):
    # pickle encounter memory error when data size is too big
    # with open(f'{pickle_name}.csv', 'rb') as f:
        # _data = joblib.load(f)
    _data = pd.read_csv(f'{pickle_name}.csv', dtype={"trade_date": "str", "symbol":"str", "session_end":"str"})

    return _data


def winsorize_data(raw_data, left=0.01, right=0.99):
    q = raw_data.quantile([left, right])
    raw_data[raw_data < q.iloc[0]] = q.iloc[0]
    raw_data[raw_data > q.iloc[1]] = q.iloc[1]

    return raw_data


def normalize_data(raw_data):
    x = (raw_data - raw_data.min()) / (raw_data.max() - raw_data.min())
    return x


def process_factor(raw_data, factor_name, key, is_winsorized=True):
    if is_winsorized:
        raw_data = raw_data[factor_name].groupby(key).apply(winsorize_data)
    else:
        raw_data = raw_data[factor_name]

    return raw_data


def preprocess_data(df_factor, factor_name, key, bar):
    # factor_name='PAT_M'
    # key='session_end'

    # 找到bar和factor的最长共有时段的开始日期、结束日期
    df_factor[key] = pd.to_datetime(df_factor[key], format='%Y-%m-%d')
    bar.trade_date = pd.to_datetime(bar.trade_date, format='%Y-%m-%d')
    df_factor.rename(columns={key:'trade_date'}, inplace=True)
    start_date = max(pd.to_datetime(config.get('start_date'), format='%Y-%m-%d'), \
        df_factor['trade_date'].min(), bar['trade_date'].min())
    end_date = min(pd.to_datetime(config.get('end_date'), format='%Y-%m-%d'), \
        df_factor['trade_date'].max(), bar['trade_date'].max())
    
    # 只选取共有时段、factor的asset部分数据,保留bar的日度数据
    df_factor = df_factor[(df_factor['trade_date'] >= start_date) \
        & (df_factor['trade_date'] <= end_date)]
    bar = bar[(bar['trade_date'] >= start_date) & (bar['trade_date'] <= end_date)]
    symbol_for_factor = df_factor.symbol.tolist()
    bar['symbol'] = bar['ts_code'].apply(lambda x: x.split('.')[0])
    bar = bar[(bar.symbol.isin(symbol_for_factor))][['trade_date', 'symbol', 'close']]
    
    # 处理因子数据
    df_factor_new = df_factor.set_index(['trade_date', 'symbol'])
    _factor = process_factor(df_factor_new, factor_name, 'trade_date', is_winsorized=True)    # Series
    factor_normalized = _factor.groupby('trade_date').apply(normalize_data)
    print(factor_normalized.head())

    # 画出因子分布图
    plt.figure(figsize=(10, 10))
    factor_normalized.hist(figsize=(12, 6), bins=50)
    plt.xlabel('Normalized Factor')
    # plt.show()
    create_output_folder(__PATH_FILE, _OutputFolder)
    plt.savefig(f"{os.path.join(__PATH_FILE, _OutputFolder, _SubFolder, 'Normalized'+factor_name)}.png")

    # 生成bar的透视图
    bar_pivot = bar.pivot_table(index='trade_date', columns='symbol', values='close')
    print(bar_pivot.head())

    return factor_normalized, bar_pivot


def find_bins(factor, quantiles):
    """
    根据factor分布，找出bins用于后续回测分层

    :param factor: processed dataframe with factor data
    :param quantiles: float or array-like, should be 0<=quantiles<=1
    """

    bins = [-1]
    _bins = factors.quantile(quantiles).round(decimals=2).tolist()
    if len(_bins) == 1:
        bins.append(_bins)
        bins.append(1)
    elif len(set(_bins)) == len(_bins):
        bins.extend(_bins)
        bins.append(1)
    else:
        raise Warning("Duplicated quantiles!")
        bins.extend(list(set(_bins)).sort())
        bins.append(1)
    
    return bins


def back_test(factor, price, auto_bins=False, quantiles=None, bins=None, periods=[1,3,6]):
    """
    :param factor: 因子数据，日期格式、股票代码格式必须与price相同，且有交集
    :param price: 股价数据，全部交易日股价数据，以用于解析交易日日期、非交易日日期
    :param auto_bins: 是否自动生成bins并划分，若为True，需要填写quantiles
    :param quantiles: 用分位数进行划分
    :param bins: 自定义分箱划分
    :param periods: 计算收益的时间间隔
    """

    if bins is None and quantiles is None:
        raise ValueError("Choose either bins or quantiles strategy!")
    elif bins is not None and quantiles is not None:
        raise ValueError("Can't fill quantiles and bins at the same time!")
    elif auto_bins and quantiles is None:
        raise ValueError("Fill quantiles for creating bins!")

    if auto_bins:
        bins = find_bins(factor, quantiles)    # 升序
        quantiles = None
        upper_quant = len(bins) - 1
        lower_quant = 1
    elif quantiles:
        quantiles_copy = copy.deepcopy(quantiles)
        quantiles_copy.extend([0., 1.])
        upper_quant = 1
        lower_quant = len(set(quantiles_copy)) - 1
    elif bins:
        upper_quant = 1
        lower_quant = len(bins) - 1

    # calculate factor and period wise forward returns
    factor_data = alphalens4m.utils.get_clean_factor_and_forward_returns(factor, price, quantiles=quantiles,
                                                                       periods=periods, max_loss=1, bins=bins)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print("Clean factor data looks like", factor_data.head())

    # Creates a tear sheet for returns analysis of a factor.
    # alphalens.tears.create_returns_tear_sheet(factor_data)

    # Computes mean returns for factor quantiles across provided forward returns columns.
    mean_return_by_q_daily, std_err = alphalens4m.performance.mean_return_by_quantile(factor_data, by_date=True)
    
    mean_return_by_q, std_err_by_q = alphalens4m.performance.mean_return_by_quantile(factor_data, by_date=False)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print("Mean return by quantiles looks like", mean_return_by_q_daily.head())
    
    # plot results
    alphalens4m.plotting.plot_quantile_returns_bar(mean_return_by_q)
    plt.savefig(f"{os.path.join(__PATH_FILE, _OutputFolder, _SubFolder, 'MeanPeriodWiseReturnByFactorQuantile')}.png")
    # plt.show()
    alphalens4m.plotting.plot_quantile_returns_violin(mean_return_by_q_daily)
    plt.savefig(f"{os.path.join(__PATH_FILE, _OutputFolder, _SubFolder, 'PeriodWiseReturnByFactorQuantile')}.png")
    # plt.show()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "\nPlot mean return done!")

    # Computes the difference between the mean returns of two quantiles.
    # Optionally, computes the standard error of this difference.
    quant_return_spread, std_err_spread = alphalens4m.performance.compute_mean_returns_spread(mean_return_by_q_daily,
                                                                                            upper_quant=upper_quant,
                                                                                            lower_quant=lower_quant,
                                                                                            std_err=std_err)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "\nMean return spread looks like", quant_return_spread.head())

    alphalens4m.plotting.plot_mean_quantile_returns_spread_time_series(quant_return_spread, std_err_spread)
    plt.savefig(f"{os.path.join(__PATH_FILE, _OutputFolder, _SubFolder, 'ReturnSpread')}.png")
    # plt.show()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "\nPlot mean return spread done!")

    period = '1M'
    alphalens4m.plotting.plot_cumulative_returns_by_quantile(mean_return_by_q_daily.iloc[:, 0], period=period)
    plt.savefig(f"{os.path.join(__PATH_FILE, _OutputFolder, _SubFolder, f'CumulativeReturnByQuantile_{period}')}.png")
    # plt.show()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "\nPlot cumulative return done!")

    # Computes period wise returns for portfolio weighted by factor values.
    ls_factor_returns = alphalens4m.performance.factor_returns(factor_data)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print(ls_factor_returns.head())

    # Creates a tear sheet for information analysis of a factor.
    # alphalens.tears.create_information_tear_sheet(factor_data)
    

    ic = alphalens4m.performance.factor_information_coefficient(factor_data)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "\nIC looks like", ic.head())
    
    alphalens4m.plotting.plot_ic_ts(ic)
    plt.savefig(f"{os.path.join(__PATH_FILE, _OutputFolder, _SubFolder, 'Ic')}.png")
    # plt.show()
    alphalens4m.plotting.plot_ic_hist(ic)
    plt.savefig(f"{os.path.join(__PATH_FILE, _OutputFolder, _SubFolder, 'IcHist')}.png")
    # plt.show()
    alphalens4m.plotting.plot_ic_qq(ic)
    plt.savefig(f"{os.path.join(__PATH_FILE, _OutputFolder, _SubFolder, 'IcQq')}.png")
    # plt.show()

    # calculate IC
    # mean_monthly_ic = alphalens4m.performance.mean_information_coefficient(factor_data, by_time='M')
    
    alphalens4m.plotting.plot_monthly_ic_heatmap(ic)
    plt.savefig(f"{os.path.join(__PATH_FILE, _OutputFolder, _SubFolder, 'MonthlyMeanIcHeatmap')}.png")
    # plt.show()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "\nPlot IC done!")

    # Creates a tear sheet for analyzing the turnover properties of a factor.
    # alphalens.tears.create_turnover_tear_sheet(factor_data)
    

    # input_periods = alphalens4m.utils.get_forward_returns_columns(
    #     factor_data.columns, require_exact_day_multiple=True,
    # ).values  # .get_values() modified by Chen Chen
    # turnover_periods = alphalens4m.utils.timedelta_strings_to_integers(input_periods)
    input_periods = factor_data.columns.tolist()[:-2]
    turnover_periods = list(map(lambda x: int(x[:-1]), input_periods))
    quantile_factor = factor_data["factor_quantile"]
    quantile_turnover = {
        p: pd.concat(
            [
                alphalens4m.performance.quantile_turnover(quantile_factor, q, p)
                for q in quantile_factor.sort_values().unique().tolist()
            ],
            axis=1,
        )
        for p in turnover_periods
    }

    index = 0
    turnover_period = turnover_periods[index]
    alphalens4m.plotting.plot_top_bottom_quantile_turnover(quantile_turnover[turnover_period], period=turnover_period)
    plt.savefig(f"{os.path.join(__PATH_FILE, _OutputFolder, _SubFolder, f'TopBottomQuantileTurnover_{input_periods[index]}')}.png")
    # plt.show()

    factor_autocorrelation = alphalens4m.performance.factor_rank_autocorrelation(factor_data, period=turnover_period)
    alphalens4m.plotting.plot_factor_rank_auto_correlation(factor_autocorrelation, period=turnover_period)
    plt.savefig(f"{os.path.join(__PATH_FILE, _OutputFolder, _SubFolder, f'AutoCorrelation_{input_periods[index]}')}.png")
    # plt.show()

    autocorrelation = pd.concat(
        [alphalens4m.performance.factor_rank_autocorrelation(factor_data, turnover_period) for turnover_period in turnover_periods],
        axis=1)
    alphalens4m.plotting.plot_turnover_table(autocorrelation, quantile_turnover)


if __name__ == '__main__':
    bar_pickle = 'daily_bar'
    write_pickle_data(bar_pickle, data_type='bar', is_run=False)
    data_bar = read_pickle_data(bar_pickle)
    data_factor = read_pickle_data(os.path.join(_OutputFolder, _SubFolder, _SubFolder))
    factors, prices = preprocess_data(data_factor, 'PAT_M', 'session_end', data_bar)
    back_test(factors, prices, auto_bins=True, quantiles=[.5, .7, .9, .95])