# -*- coding: utf-8 -*-

__auth__ = 'Chen Chen'

import sys
import numpy as np
import pandas as pd
import tushare as ts
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from patent_count_in_session import get_session_list
from helper import *
import matplotlib.pyplot as plt

__PATH_FILE = os.path.dirname(__file__)
_ConfigFolder = 'Config'
_ConfigFile = 'config.json'
_InputFolder = 'Input'
_OutputFolder = 'Output'
_Script = os.path.basename(__file__).rstrip('.py')
config = get_config(__PATH_FILE, _ConfigFolder, _ConfigFile)


def get_last_trade_date(date, months):
    session_start_date_after_months = (pd.to_datetime(date) + relativedelta(months=months, day=1)).strftime('%Y%m%d')
    session_end_date_after_months = (pd.to_datetime(date) + relativedelta(months=months, day=31)).strftime('%Y%m%d')
    # update session start and end date with last trading date from tushare
    df_trade_cal = pro.trade_cal(start_date=session_start_date_after_months,
                                 end_date=session_end_date_after_months)
    trading_dates = df_trade_cal[df_trade_cal['is_open'] == 1]['cal_date'].tolist()
    if not trading_dates:  # if date is close to today, session_end_date_after_months might be not available on tushare
        return session_end_date_after_months
    last_trading_date = trading_dates[-1]

    time.sleep(1)  # _maximum 60 request quotas per _minute

    return last_trading_date


@func_timer
def kickoff_new_company_in_certain_time(session_end_date, df_stock_basic):
    # get listed company info
    df_stock_basic_listed = df_stock_basic
    # kick out new stocks listed in certain time
    kickoff_days = int(config.get('kickoff_days'))
    session_back_date = (pd.to_datetime(session_end_date) - relativedelta(days=kickoff_days)).strftime("%Y%m%d")
    _df_stock_basic_listed_after_kickoff = df_stock_basic_listed[df_stock_basic_listed['list_date'] < session_back_date]

    return _df_stock_basic_listed_after_kickoff.ts_code.tolist()


@func_timer
def select_stock_based_on_session(session_end, df_stock_basic, df_namechange, df_qfq):
    """
    Filter stocks listed 1 year ago and not ST/*ST/SST/S*ST on session end date
    S：还没有进行或完成股改的股票；
    ST：这是对连续两个会计年度都出现亏损的公司施行的特别处理；
    *ST：是连续三年亏损，有退市风险的意思，购买这样的股票要有比较好的基本面分析能力；
    S*ST：指公司经营连续三年亏损，进行退市预警和还没有完成股改；
    SST：指公司经营连续二年亏损进行的特别处里和还没有完成股改；
    NST：经过重组或股改重新恢复上市的ST股。
    :param config_json: config
    :param session_end: last trade day of a session
    :param df_stock_basic: stock information of establish
    :param df_namechange: stock name changing information, e.g. 摘星，改名，股改，ST，*ST etc.
    :param df_qfq: back adjust bar data
    :return: stocks_filtered
    """
    # 1. kick off new stocks less than 1 year
    stock_list_after_kickoff = kickoff_new_company_in_certain_time(session_end, df_stock_basic)
    n1 = len(stock_list_after_kickoff)

    # 2. st related stocks
    # the way to determine whether a stock is ST/*ST/SST/S*ST by checking <name> field of df_namechange.
    # if ST in its name and the date to check is between start_date and end_date, the stock is a ST/*ST/SST/S*ST stock.
    df_st = df_namechange[
        (df_namechange['start_date'] < session_end) & (df_namechange['end_date'] >= session_end) & (
            df_namechange['name'].str.contains('ST'))]
    stocks_st_on_session_end = df_st.ts_code.tolist()
    n2 = len(stocks_st_on_session_end)

    # 3. kick off st related stocks
    stocks_filtered_candidates = [stock for stock in stock_list_after_kickoff if stock not in stocks_st_on_session_end]
    n3 = len(stocks_filtered_candidates)

    # 4. kick off pending stocks
    # if stocks can not find in df_qfq when trade_date == session_end, it's suspended. kick them out.
    trading_stocks_on_session_end = df_qfq[df_qfq.trade_date == session_end].ts_code.tolist()
    stocks_filtered = [stock for stock in stocks_filtered_candidates if stock in trading_stocks_on_session_end]
    n4 = len(stocks_filtered)

    emit_log(config, _Script, f"{sys._getframe().f_code.co_name}|On {session_end}: {n4} stocks are selected. "
             f"{n1} stocks found after new stock kickoff; {n2} ST/*ST stock found; "
             f"{n3} stocks found after ST/*ST kickoff; {n4} stocks found after suspend kickoff.")

    return stocks_filtered


@func_timer
def calculate_excess_return(df_basic, df_namechange, df_qfq):
    global pro
    pro = ts.pro_api(token=config.get('token'))
    # get session list
    session_list = get_session_list(months=1)
    session_period_dict = {'M': 1, 'Q': 3, 'SA': 6, 'A': 12}

    df_er_all = pd.DataFrame()
    for session in session_list:
        session_end = session[-1]
        stocks_session_filtered = select_stock_based_on_session(session_end, df_basic, df_namechange, df_qfq)
        df_qfq_session = df_qfq[df_qfq['trade_date'] == session_end]
        # kick off new/ST/pending stocks
        df_qfq_session_filtered = df_qfq_session[
            df_qfq_session.apply(lambda row: row.ts_code in stocks_session_filtered, axis=1)]
        df_qfq_session_filtered = df_qfq_session_filtered.copy()
        df_qfq_session_filtered['session_date'] = session_end
        df_qfq_session_period = df_qfq_session_filtered[['ts_code', 'close', 'total_mv', 'session_date']]
        shibor = pro.shibor(start_date=session_end, end_date=session_end)
        shibor.rename(columns={'1y': '12m'}, inplace=True)
        for k, v in session_period_dict.items():
            # get last trade date for future
            last_trade_day_future = get_last_trade_date(session_end, v)  
            df_qfq_session_future = df_qfq[df_qfq['trade_date'] == last_trade_day_future]
            df_qfq_session_future_filtered = df_qfq_session_future[
                df_qfq_session_future.apply(lambda row: row.ts_code in stocks_session_filtered, axis=1)][
                ['ts_code', 'close', 'total_mv']]
            # merge current and future session
            df_qfq_session_period = pd.merge(df_qfq_session_period, df_qfq_session_future_filtered, how='left',
                                             on='ts_code', suffixes=('', f"_{v}m"))
            yield_return_session = (df_qfq_session_period[f"close_{v}m"].to_numpy() / df_qfq_session_period[
                'close'].to_numpy() - 1) * 100
            yield_return_session = pd.DataFrame({f"{v}m": yield_return_session})
            df_qfq_session_period[f"er_{v}m"] = yield_return_session[f"{v}m"] - shibor[f"{v}m"].values.tolist()[0]
            emit_log(config, _Script, f"{sys._getframe().f_code.co_name}|{k}: {session_end}, {last_trade_day_future}")

        df_er_all = pd.concat([df_er_all, df_qfq_session_period], axis=0, ignore_index=True)

    columns_excess_return = ['ts_code', 'session_date'] + [f"er_{v}m" for v in session_period_dict.values()] + [
        f"total_mv_{v}m" for v in session_period_dict.values()]
    df_excess_return = df_er_all[columns_excess_return]
    # convert ts_code to symbol for consistence with factor
    df_excess_return = df_excess_return.copy()
    df_excess_return['ts_code'] = df_excess_return['ts_code'].apply(lambda x: x.split('.')[0])
    df_excess_return.rename(columns={'ts_code': 'symbol'}, inplace=True)

    return df_excess_return


@func_timer
def process_factor(df_patent, df_rd_cost, transform=True, z=True):
    df_rd_cost.rename(columns={'RD_M(t-1)': 'RD_M', 'RD_Q(t-1)': 'RD_Q', 'RD_SA(t-1)': 'RD_SA', 'RD_A(t-1)': 'RD_A'},
                      inplace=True)
    df_rd_cost[['RD_M', 'RD_Q', 'RD_SA', 'RD_A']] = df_rd_cost[['RD_M', 'RD_Q', 'RD_SA', 'RD_A']].applymap(
        lambda x: np.nan if x == 0 else x / 1E+8)
    df_factor = pd.merge(df_patent, df_rd_cost, how='left', on=['symbol', 'session_end'])
    session_period_dict = {'M': 1, 'Q': 3, 'SA': 6, 'A': 12}
    for key in session_period_dict.keys():
        df_factor[f"EFF_{key}"] = round(df_factor[f"PAT_{key}"]/df_factor[f"RD_{key}"], 4)
    columns_eff = ['symbol', 'session_end'] + [f"PAT_{key}" for key in session_period_dict.keys()] + [
        f"EFF_{key}" for key in session_period_dict.keys()]
    df_factor_transfrom = gen_factor(df_factor[columns_eff], transform=transform, z=z)

    return df_factor_transfrom


def _transform_outliers(array, method='mad'):
    array_copy = array.copy()
    if method == 'std':
        """
        transform outliers greater than 3 std between 3 and 5 std
        """
        # TODO could try smaller std, e.g. 2-3 std
        # assert not array.isnull().all()
        if array.isnull().all():
            return array
        _mean = np.nanmean(array)
        _std = np.nanstd(array)
        _min = np.nanmin(array)
        _max = np.nanmax(array)
        for i in range(len(array)):
            # print(i, len(array_copy))
            x = array.iloc[i]
            if x > _mean + 3 * _std:
                y = _mean + 3 * _std + 2 * _std * (x - _mean - 3 * _std) / (_max - _mean - 3 * _std)
            elif x < _mean - 3 * _std:
                y = _mean - 3 * _std - 2 * _std * (x - (_mean - 3 * _std)) / (_min - (_mean - 3 * _std))
            else:
                y = x
            array_copy.iloc[i] = y
    elif method == 'mad':
        """
        transform outliers greater than 3 mad between 3 and 5 mad
        """
        if array.isnull().all():
            return array
        _median = np.nanmedian(array)
        _ad = abs(array - _median)
        _mad = np.nanmedian(_ad)
        _min = np.nanmin(array)
        _max = np.nanmax(array)
        _constant = 1.4816
        _pseudo_std = _constant * _mad
        for i in range(len(array)):
            x = array.iloc[i]
            if x > _median + 3 * _pseudo_std:
                y = _median + 3 * _pseudo_std + 2 * _pseudo_std * (x - _median - 3 * _pseudo_std) / (
                            _max - _median - 3 * _pseudo_std)
            elif x < _median - 3 * _pseudo_std:
                y = _median - 3 * _pseudo_std - 2 * _pseudo_std * (x - (_median - 3 * _pseudo_std)) / (
                            _min - (_median - 3 * _pseudo_std))
            else:
                y = x
            array_copy.iloc[i] = y
    else:
        emit_log(config, _Script, f'method not recognize, please use std or mad method.')

    return array_copy


@func_timer
def gen_factor(df_eff, transform=True, z=True, method='std'):
    columns = df_eff.columns.tolist()
    if 'symbol' in columns:
        columns.remove('symbol')
    if 'session_end' in columns:
        columns.remove('session_end')
    # transform outliers
    if transform:
        df_copy = df_eff.copy()
        for column in columns:
            df_copy[f'{column}_Trans'] = df_copy.groupby('session_end')[column].apply(_transform_outliers,
                                                                                      method=method)

        # if transform_show:
        #     for i, f in enumerate(columns):
        #         plt.figure(figsize=(10, 6), dpi=80)
        #         plt.figure(i + 1)
        #         ax1 = plt.subplot(1, 2, 1)
        #         ax1.hist(df_eff[f][df_eff['session_end'] == '20181228'], bins=40)
        #         ax1.set_title("处理异常值前{0}时间截面下{1}因子的分布情况".format('20181228', f))
        #         ax2 = plt.subplot(1, 2, 2)
        #         ax2.hist(df_copy[f][df_copy['session_end'] == '20181228'], bins=40)
        #         ax2.set_title("处理异常值后{0}时间截面下{1}因子的分布情况".format('20181228', f))
        #     plt.tight_layout()
        #     plt.show()

        df_eff = df_copy

    # standardize with z-score
    if z:
        df_copy = df_eff.copy()
        columns = df_copy.columns.tolist()
        columns.remove('symbol')
        columns.remove('session_end')
        columns_copy = deepcopy(columns)
        # only process transformed columns
        for column in columns_copy:
            if 'Trans' not in column:
                columns.remove(column)
        # z-score
        df_copy[columns] = df_copy.groupby('session_end')[columns].apply(
                                      lambda x: (x - np.nanmean(x)) / np.nanstd(x))
        df_eff = df_copy

    return df_eff


@func_timer
def main():
    emit_log(config, _Script, f"Program starts...")
    # part 1: rd efficiency processing, will use output from data_tushare
    # read back adjust data
    df_qfq = pd.read_csv(os.path.join(__PATH_FILE, _OutputFolder, 'stock_bar_marketcap.csv'), dtype={'trade_date': str})
    # read stock_basic information
    df_basic = pd.read_csv(os.path.join(__PATH_FILE, _OutputFolder, 'stock_basic_overall.csv'),
                           dtype={'list_date': str})
    # read name change information
    df_namechange = pd.read_csv(os.path.join(__PATH_FILE, _OutputFolder, 'stock_namechange.csv'),
                                dtype={'start_date': str, 'end_date': str})
    # process excess return
    df_er = calculate_excess_return(df_basic, df_namechange, df_qfq)
    # save the output
    df_er.to_csv(os.path.join(__PATH_FILE, _OutputFolder, f"excess_return.csv"), encoding='utf-8', index=False)

    # part 2: factor processing, will use patent and rd data from BBD warehouse
    # read patent data
    df_pat = pd.read_csv(os.path.join(__PATH_FILE, _OutputFolder, 'patent_count_session.csv'),
                         dtype={'symbol': str, 'session_end': str})
    # read research and exploration data
    df_rd = pd.read_csv(os.path.join(__PATH_FILE, _OutputFolder, 'rd_cost.csv'),
                        dtype={'symbol': str, 'session_end': str})
    df_factor = process_factor(df_pat, df_rd, transform=False, z=False)     # do NOT transform here, do it in modeling
    df_factor.to_csv(os.path.join(__PATH_FILE, _OutputFolder, 'factor.csv'), encoding='utf-8', index=False)

    emit_log(config, _Script, f"All finished")

    pass


if __name__ == '__main__':
    main()
