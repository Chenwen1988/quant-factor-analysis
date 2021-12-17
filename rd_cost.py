# -*- coding: utf-8 -*-

__auth__ = 'Chen Chen'

import sys
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from patent_count_in_session import get_session_list
from helper import *

__PATH_FILE = os.path.dirname(__file__)
_ConfigFolder = 'Config'
_ConfigFile = 'config.json'
_InputFolder = 'Input'
_OutputFolder = 'Output'
_Script = os.path.basename(__file__).rstrip('.py')
config = get_config(__PATH_FILE, _ConfigFolder, _ConfigFile)


@func_timer
def process_rd_data():
    # read raw data of r&d and company
    df_rd = pd.read_csv(os.path.join(__PATH_FILE, _InputFolder, 'yanfa.csv'),
                        usecols=['bbd_qyxx_id', 'report_date', 'r_and_d_cost'])
    df_company = pd.read_csv(os.path.join(__PATH_FILE, _InputFolder, 'company_list_withid.csv'),
                             usecols=['symbol', 'bbd_qyxx_id'], dtype={'symbol': str})
    # merge data with bbd_qyxx_id
    df_rd = pd.merge(left=df_company, right=df_rd, how='left', on='bbd_qyxx_id')
    # convert date format
    df_rd['report_date'] = pd.to_datetime(df_rd['report_date'])
    # add a new column of period
    df_rd['quarter'] = pd.PeriodIndex(df_rd.report_date, freq='Q')
    df_rd.drop_duplicates(inplace=True)
    # remove companies with no r&d cost
    df_rd = df_rd[df_rd['r_and_d_cost'] != '--']
    # only select data after start date
    df_rd = df_rd[df_rd['report_date'] >= config.get('start_date')]

    # somehow dirty data exist, remove companies with multiple records
    df = df_rd.groupby(['bbd_qyxx_id', 'report_date']).count().reset_index()
    df = df[df['r_and_d_cost'] > 1]
    bbd_id_with_multi_records = df.bbd_qyxx_id.drop_duplicates().tolist()
    df_rd = df_rd[~df_rd.bbd_qyxx_id.isin(bbd_id_with_multi_records)]

    # if r&d dataframe has very early data, only select part of data
    today = datetime.datetime.today()
    start_date = today - relativedelta(years=config.get('time_len') + 2)  # +2 for safe boundary
    df_rd = df_rd[df_rd['report_date'] >= start_date]
    # use bbd_qyxx_id instead of company_name, otherwise the company changed name will have two records after groupby
    df_rd_pivot = df_rd.pivot_table(index=['symbol', 'bbd_qyxx_id'], columns='quarter', values='r_and_d_cost',
                                    aggfunc=np.sum)

    # TODO maybe only select companies with enough data

    # forward fill nan
    df_rd_pivot_fillna_ffill = df_rd_pivot.fillna(method='ffill', axis=1)
    # backward fill nan to ensure no nan in the dataframe
    df_rd_pivot_fillna_fill_all = df_rd_pivot_fillna_ffill.fillna(method='bfill', axis=1)

    return df_rd_pivot_fillna_fill_all


@func_timer
def calculate_year_long_cost(df_rd, save_csv=''):
    """
        r&d session cost always uses year long cost, the only difference is how to cut period
    """
    # define session dictionary
    session_period_dict = {'M': 1, 'Q': 3, 'SA': 6, 'A': 12}
    df_rd_session = pd.DataFrame()
    # outer loop: period
    for k, v in session_period_dict.items():
        # due to r&d data is published by quarter, use Q data for M
        if k == 'M':
            continue
        # get session list
        list_session_tuple = get_session_list(session_period_dict[k])[:-1]
        df_tmp_session = pd.DataFrame()
        # inner loop: session
        for session in list_session_tuple:
            df_tmp = pd.DataFrame()
            session_end = session[-1]
            if k == 'Q':
                """
                    例如t=2019Q1：
                    RD_Q(t-1)=r_and_d_cost(2018/09/30) + r_and_d_cost(2017/12/31) - r_and_d_cost(2017/09/30)

                """
                session_period_last = str(
                    pd.PeriodIndex([pd.to_datetime(session_end) - relativedelta(months=v)], freq='Q')[0])
                session_period_last_year = str(
                    pd.PeriodIndex([pd.to_datetime(session_end) - relativedelta(years=1, month=12)], freq='Q')[0])
                session_period_last_in_last_year = str(
                    pd.PeriodIndex([pd.to_datetime(session_end) - relativedelta(years=1, months=v)], freq='Q')[0])
                # if session_period_last == '2020Q2':
                #     continue
                df = df_rd[session_period_last].astype('float') + df_rd[session_period_last_year].astype('float') -\
                     df_rd[session_period_last_in_last_year].astype('float')
            elif k == 'A':
                session_period_last_year = str(
                    pd.PeriodIndex([pd.to_datetime(session_end) - relativedelta(years=1, month=12)], freq='Q')[0])
                df = df_rd[session_period_last_year].astype('float')
            else:  # k == SA:
                """
                    例如t=2019SA1：
                    RD_SA(t-1) = r_and_d_cost(2019/06/30) + r_and_d_cost(2018/12/31) - r_and_d_cost(2018/06/30)

                    t=2019SA2等价于2019A
                """
                if pd.to_datetime(session_end).month >= 7:  # second half
                    session_period_last = str(
                        pd.PeriodIndex([pd.to_datetime(session_end) - relativedelta(month=6)], freq='Q')[0])
                    session_period_last_year = str(
                        pd.PeriodIndex([pd.to_datetime(session_end) - relativedelta(years=1, month=12)], freq='Q')[0])
                    session_period_last_in_last_year = str(
                        pd.PeriodIndex([pd.to_datetime(session_end) - relativedelta(years=1, month=6)], freq='Q')[0])
                    df = df_rd[session_period_last].astype('float') + df_rd[session_period_last_year].astype('float') -\
                         df_rd[session_period_last_in_last_year].astype('float')
                else:   # fist half
                    session_period_last_year = str(
                        pd.PeriodIndex([pd.to_datetime(session_end) - relativedelta(years=1, month=12)], freq='Q')[0])
                    df = df_rd[session_period_last_year].astype('float')
            emit_log(config, _Script, f"{sys._getframe().f_code.co_name}|{k}:{session_end} processing ...")
            df_tmp[f'RD_{k}(t-1)'] = df
            df_tmp['symbol'] = df_rd.index.get_level_values(0)
            df_tmp['session_end'] = session_end
            df_tmp_session = pd.concat([df_tmp_session, df_tmp], axis=0, ignore_index=True)
        # add symbol when comes up at 1st time
        if 'symbol' not in df_rd_session.columns:
            df_rd_session = pd.concat([df_rd_session, df_tmp_session], axis=1)
        else:
            df_rd_session = pd.concat([df_rd_session, df_tmp_session[f'RD_{k}(t-1)']], axis=1)
    # due to r&d data is published by quarter, use Q data for M
    df_rd_session['RD_M(t-1)'] = df_rd_session['RD_Q(t-1)']
    # adjust column order
    fields = [f'RD_{key}(t-1)' for key in session_period_dict.keys()]
    fields.insert(0, 'symbol')
    fields.append('session_end')
    df_rd_session = df_rd_session[fields]

    # whether save to csv file
    if save_csv:
        create_output_folder(__PATH_FILE, _OutputFolder)
        df_rd_session.to_csv(os.path.join(__PATH_FILE, _OutputFolder, save_csv), index=False)


def main():
    emit_log(config, _Script, f"Program starts...")
    # process r&d cost data
    df_rd_from_file = process_rd_data()
    # r&d session cost always uses year long cost, the only difference is how to cut period
    calculate_year_long_cost(df_rd_from_file, save_csv='rd_cost.csv')

    emit_log(config, _Script, f"All finished")


if __name__ == '__main__':
    main()
