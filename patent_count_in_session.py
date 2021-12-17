# -*- coding: utf-8 -*-
"""

"""
__auth__ = 'Chen Chen'

import sys
import pandas as pd
import tushare as ts
from dateutil.relativedelta import relativedelta
from helper import *

__PATH_FILE = os.path.dirname(__file__)
_ConfigFolder = 'Config'
_ConfigFile = 'config.json'
_InputFolder = 'Input'
_OutputFolder = 'Output'
_Script = os.path.basename(__file__).rstrip('.py')
config = get_config(__PATH_FILE, _ConfigFolder, _ConfigFile)


@func_timer
def get_session_list(months=1):
    # if end_date is not specified in config.json, end_date is today
    if config.get('end_date') == -1:
        end_date = datetime.datetime.today()
    else:
        end_date = pd.to_datetime(config.get('end_date'))
    # determine the number of total session
    total_session = (config.get('time_len') + 1) * 12  # +1 ensure 1st session has patent count
    # generate start_date/end_date of sessions
    session_list_by_month = [(end_date - relativedelta(months=i)) for i in range(1, total_session + 1)]
    session_start_date_list = [(session + relativedelta(day=1)).strftime('%Y%m%d') for session in session_list_by_month]
    session_end_date_list = [(session + relativedelta(day=31)).strftime('%Y%m%d') for session in session_list_by_month]
    # update session start and end date with trade_cal from tushare
    """
    接口：trade_cal
    描述：获取各大交易所交易日历数据,默认提取的是上交所
    输入参数：
    名称	    类型	必选	描述
    exchange	str	    N	    交易所 SSE上交所, SZSE深交所, CFFEX 中金所, SHFE 上期所, CZCE 郑商所, DCE 大商所, INE 上能源, IB 银行间, XHKG 港交所
    start_date	str 	N	    开始日期
    end_date	str	    N	    结束日期
    is_open	    str	    N	    是否交易 '0'休市 '1'交易
    
    输出参数：
    名称	        类型	默认显示	    描述
    exchange	    str	    Y	        交易所 SSE上交所 SZSE深交所
    cal_date	    str	    Y	        日历日期
    is_open	        str	    Y	        是否交易 0休市 1交易
    pretrade_date	str 	N	        上一个交易日
    
        exchange    cal_date        is_open
    0   SSE         20180101        0
    1   SSE         20180102        1
    2   SSE         20180103        1
    """
    pro = ts.pro_api(token=config.get('token'))
    df_trade_cal = pro.trade_cal(start_date=session_start_date_list[-1], end_date=session_end_date_list[0])
    df_trade_cal['cal_date_strptime'] = pd.to_datetime(df_trade_cal['cal_date'], format='%Y%m%d')
    session_end_date_list_update = list()
    session_start_date_list_update = list()
    for i in range(total_session):
        # get start and end dates for each session
        start_date = pd.to_datetime(session_start_date_list[i], format='%Y%m%d')
        end_date = pd.to_datetime(session_end_date_list[i], format='%Y%m%d')
        # get trade date from tushare for this session
        df_trade_cal_select = df_trade_cal[(df_trade_cal['cal_date_strptime'] >= start_date)
                                           & (df_trade_cal['cal_date_strptime'] <= end_date)]
        first_trading_date = df_trade_cal_select[df_trade_cal_select['is_open'] == 1]['cal_date'].tolist()[0]
        session_start_date_list_update.append(first_trading_date)
        last_trading_date = df_trade_cal_select[df_trade_cal_select['is_open'] == 1]['cal_date'].tolist()[-1]
        session_end_date_list_update.append(last_trading_date)
    # calculate session tuples for different periods based on argument months
    session_tuple_list = [(session_start_date_list_update[i + months - 1], session_end_date_list_update[i])
                          for i in range(config.get('time_len') * 12)]
    session_tuple_list.reverse()

    return session_tuple_list


@func_timer
def count_patent_for_session(df_patent, dict_session, save_csv=''):
    # empty dataframe to store patent count
    df_temp_session = pd.DataFrame()
    df_patent_count_session = df_patent.groupby('symbol').count()
    # outer loop: period
    for k, v in dict_session.items():
        # empty temporary dataframe to store patent count of certain period
        df_temp_company = pd.DataFrame()
        # inner loop: session
        for session in v:
            # add patent counts for each period session
            df_patent['publidate'] = pd.to_datetime(df_patent['publidate'])
            session_start = pd.to_datetime(session[0])
            session_end = pd.to_datetime(session[1])
            # select data between start and end dates, then count
            df = df_patent[(df_patent['publidate'] >= session_start) & (df_patent['publidate'] <= session_end)] \
                .groupby('symbol').agg({'publidate': 'count'}).reset_index()
            df.columns = ['symbol', f'PAT_{k}']
            # in order to keep every single company in df
            df = pd.merge(df_patent_count_session, df, how='left', on='symbol').drop('publidate', 1)
            # fill 0 for those company with no patent count
            df.fillna(0, inplace=True)
            df[f'PAT_{k}'] = df[f'PAT_{k}'].astype('int')
            # label end date for the session
            df['session_end'] = session[-1]
            # concatenate sessions
            df_temp_company = pd.concat([df_temp_company, df], axis=0, ignore_index=True)
        # add symbol when comes up at 1st time
        if 'symbol' not in df_temp_session.columns:
            df_temp_session = pd.concat([df_temp_session, df_temp_company], axis=1)
        else:
            df_temp_session = pd.concat([df_temp_session, df_temp_company[[f'PAT_{k}']]], axis=1)
    # adjust column order
    fields = [f'PAT_{key}' for key in dict_session.keys()]
    fields.insert(0, 'symbol')
    fields.append('session_end')
    df_temp_session = df_temp_session[fields]

    # whether save to csv file
    if save_csv:
        create_output_folder(__PATH_FILE, _OutputFolder)
        df_temp_session.to_csv(os.path.join(__PATH_FILE, _OutputFolder, save_csv), index=False)
        emit_log(config, _Script, f"File saved.")

    # return df_temp_session


@func_timer
def main():
    emit_log(config, _Script, f"Program starts...")
    # define session dictionary
    session_period_dict = {'M': 1, 'Q': 3, 'SA': 6, 'A': 12}
    session_tuple_dict = dict()
    # store session tuple list in the dictionary
    for k, v in session_period_dict.items():
        df_session_tuple = get_session_list(session_period_dict[k])
        session_tuple_dict[k] = df_session_tuple
        emit_log(config, _Script, f"{sys._getframe().f_code.co_name}|{k}: {len(df_session_tuple)}, {df_session_tuple}")

    # read in patent raw data zhuanli.csv and company info company_list_withid.csv, which is from data warehouse
    df_patent = pd.read_csv(os.path.join(__PATH_FILE, _InputFolder, 'zhuanli.csv'))
    df_company = pd.read_csv(os.path.join(__PATH_FILE, _InputFolder, 'company_list_withid.csv'))
    df_company.symbol = df_company.symbol.astype(str).map(lambda x: x.zfill(6))
    # update df_patent, only two fields needed
    df_patent = pd.merge(left=df_company, right=df_patent, how='left', on='bbd_qyxx_id')[['symbol', 'publidate']]

    # count patent for each session
    count_patent_for_session(df_patent, session_tuple_dict, save_csv='patent_count_session.csv')
    emit_log(config, _Script, f"All finished")


if __name__ == '__main__':
    main()
