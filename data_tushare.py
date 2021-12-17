# -*- coding: utf-8 -*-
"""
    1. query data for Listed/Delisted/Pending from Tushare and save to csv file
    2. query back adjust (qfq) data and save to csv file
    3. query st/pt stocks and save to csv file
    basic_information/qfq/stpt files are used to calculate excess return in factor_processing.py
"""
__auth__ = 'Chen Chen'

import tushare as ts
import pandas as pd
from helper import *

__PATH_FILE = os.path.dirname(__file__)
_ConfigFolder = 'Config'
_ConfigFile = 'config.json'
_InputFolder = 'Input'
_OutputFolder = 'Output'
_Script = os.path.basename(__file__).rstrip('.py')
config = get_config(__PATH_FILE, _ConfigFolder, _ConfigFile)


def get_stock_basic_listed(fields):
    """
    描述：获取基础信息数据，包括股票代码、名称、上市日期、退市日期等

    输入参数:
    名称	    类型	    必选	    描述
    is_hs	    str	        N	        是否沪深港通标的：N否 H沪股通 S深股通
    list_status	str	        N	        上市状态：L上市 D退市 P暂停上市，默认L
    exchange	str	        N	        交易所: SSE上交所 SZSE深交所 HKEX港交所(未上线)

    输出参数:
    名称	    类型	    描述
    ts_code	    str	        TS代码
    symbol	    str	        股票代码
    name	    str	        股票名称
    area	    str	        所在地域
    industry	str	        所属行业
    fullname	str	        股票全称
    enname	    str	        英文全称
    market	    str	        市场类型 （主板/中小板/创业板/科创板）
    exchange	str	        交易所代码
    curr_type	str	        交易货币
    list_status	str	        上市状态： L上市 D退市 P暂停上市
    list_date	str	        上市日期
    delist_date	str	        退市日期
    is_hs	    str	        是否沪深港通标的，N否 H沪股通 S深股通

    e.g.
          ts_code       symbol      name        area        industry        list_date
    0     000001.SZ     000001      平安银行    深圳         银行            19910403
    1     000002.SZ     000002      万科A       深圳         全国地产        19910129
    2     000004.SZ     000004      国农科技    深圳         生物制药        19910114
    6     000008.SZ     000008      神州高铁    北京         运输设备        19920507
    """
    token = config.get('token')
    pro = ts.pro_api(token=token, timeout=float(config.get('timeout')))
    _df_stock_basic = pro.stock_basic(list_status='L', fields=fields)

    return _df_stock_basic


def get_stock_basic_delisted(fields):
    """
    描述：获取基础信息数据，包括股票代码、名称、上市日期、退市日期等

    输入参数:
    名称	    类型	    必选	    描述
    is_hs	    str	        N	        是否沪深港通标的：N否 H沪股通 S深股通
    list_status	str	        N	        上市状态：L上市 D退市 P暂停上市，默认L
    exchange	str	        N	        交易所: SSE上交所 SZSE深交所 HKEX港交所(未上线)

    输出参数:
    名称	    类型	    描述
    ts_code	    str	        TS代码
    symbol	    str	        股票代码
    name	    str	        股票名称
    area	    str	        所在地域
    industry	str	        所属行业
    fullname	str	        股票全称
    enname	    str	        英文全称
    market	    str	        市场类型 （主板/中小板/创业板/科创板）
    exchange	str	        交易所代码
    curr_type	str	        交易货币
    list_status	str	        上市状态： L上市 D退市 P暂停上市
    list_date	str	        上市日期
    delist_date	str	        退市日期
    is_hs	    str	        是否沪深港通标的，N否 H沪股通 S深股通

    e.g.
          ts_code       symbol      name        area        industry        list_date
    0     000001.SZ     000001      平安银行    深圳         银行            19910403
    1     000002.SZ     000002      万科A       深圳         全国地产        19910129
    2     000004.SZ     000004      国农科技    深圳         生物制药        19910114
    6     000008.SZ     000008      神州高铁    北京         运输设备        19920507
    """
    token = config.get('token')
    pro = ts.pro_api(token=token, timeout=float(config.get('timeout')))
    _df_stock_basic = pro.stock_basic(list_status='D', fields=fields)

    return _df_stock_basic


def get_stock_basic_pending(fields):
    """
    描述：获取基础信息数据，包括股票代码、名称、上市日期、退市日期等

    输入参数:
    名称	    类型	    必选	    描述
    is_hs	    str	        N	        是否沪深港通标的：N否 H沪股通 S深股通
    list_status	str	        N	        上市状态：L上市 D退市 P暂停上市，默认L
    exchange	str	        N	        交易所: SSE上交所 SZSE深交所 HKEX港交所(未上线)

    输出参数:
    名称	    类型	    描述
    ts_code	    str	        TS代码
    symbol	    str	        股票代码
    name	    str	        股票名称
    area	    str	        所在地域
    industry	str	        所属行业
    fullname	str	        股票全称
    enname	    str	        英文全称
    market	    str	        市场类型 （主板/中小板/创业板/科创板）
    exchange	str	        交易所代码
    curr_type	str	        交易货币
    list_status	str	        上市状态： L上市 D退市 P暂停上市
    list_date	str	        上市日期
    delist_date	str	        退市日期
    is_hs	    str	        是否沪深港通标的，N否 H沪股通 S深股通

    e.g.
          ts_code       symbol      name        area        industry        list_date
    0     000001.SZ     000001      平安银行    深圳         银行            19910403
    1     000002.SZ     000002      万科A       深圳         全国地产        19910129
    2     000004.SZ     000004      国农科技    深圳         生物制药        19910114
    6     000008.SZ     000008      神州高铁    北京         运输设备        19920507
    """
    token = config.get('token')
    pro = ts.pro_api(token=token, timeout=float(config.get('timeout')))
    _df_stock_basic = pro.stock_basic(list_status='P', fields=fields)

    return _df_stock_basic


def get_daily_bar_from_tushare():
    token = config.get('token')
    start_date = config.get('start_date')
    end_date = config.get('end_date')
    pro = ts.pro_api(token=token, timeout=float(config.get('timeout')))
    _df_daily_bar = pro.daily(ts_code='000001.sz', start_date=start_date, end_date=end_date)
    # print(_df_daily_bar.head())
    _df_daily_bar.set_index("trade_date", drop=True, inplace=True)
    _df_daily_bar.sort_index(inplace=True)

    return _df_daily_bar


def concat_stock_basic(fields):
    """
    :param fields: 需要输出的字段
    concatenate 所有上市公司、退市公司、停牌公司股票数据
    :return: dataframe
    """
    # get listed company info
    df_stock_basic_listed = get_stock_basic_listed(fields)
    # print(df_stock_basic_listed)
    # get delisted company info
    df_stock_basic_delisted = get_stock_basic_delisted(fields)
    # print(df_stock_basic_delisted)
    # get pending company info
    df_stock_basic_pending = get_stock_basic_pending(fields)
    # print(df_stock_basic_pending)
    _df_stock_basic_overall = pd.concat([df_stock_basic_listed, df_stock_basic_delisted, df_stock_basic_pending],
                                        axis=0, ignore_index=True)

    return _df_stock_basic_overall


@func_timer
def get_qfq_bar_data(code_list):
    """
    描述：目前整合了股票（未复权、前复权、后复权）、指数、数字货币、ETF基金、期货、期权的行情数据，
    未来还将整合包括外汇在内的所有交易行情数据，同时提供分钟数据。不同数据对应不同的积分要求，具体请参阅每类数据的文档说明。

    输入参数：
    名称	    类型	    必选	    描述
    ts_code	    str	        Y	        证券代码
    api	        str         N	        pro版api对象，如果初始化了set_token，此参数可以不需要
    start_date	str	        N	        开始日期 (格式：YYYYMMDD，提取分钟数据请用2019-09-01 09:00:00这种格式)
    end_date	str	        N	        结束日期 (格式：YYYYMMDD)
    asset	    str	        Y	        资产类别：E股票 I沪深指数 C数字货币 FT期货 FD基金 O期权 CB可转债（v1.2.39），默认E
    adj	        str	        N	        复权类型(只针对股票)：None未复权 qfq前复权 hfq后复权 , 默认None
    freq	    str	        Y	        数据频度 ：支持分钟(min)/日(D)/周(W)/月(M)K线，其中1min表示1分钟（类推1/5/15/30/60分钟） ，默认D。对于分钟数据有600积分用户可以试用（请求2次），正式权限请在QQ群私信群主或积分管理员。
    ma	        list	    N	        均线，支持任意合理int数值。注：均线是动态计算，要设置一定时间范围才能获得相应的均线，比如5日均线，开始和结束日期参数跨度必须要超过5日。目前只支持单一个股票提取均线，即需要输入ts_code参数。
    factors	    list	    N	        股票因子（asset='E'有效）支持 tor换手率 vr量比
    adjfactor	str	        N	        复权因子，在复权数据时，如果此参数为True，返回的数据中则带复权因子，默认为False。 该功能从1.2.33版本开始生效

    输出指标：
    具体输出的数据指标可参考各行情具体指标：
    股票Daily：https://tushare.pro/document/2?doc_id=27
    基金Daily：https://tushare.pro/document/2?doc_id=127
    期货Daily：https://tushare.pro/document/2?doc_id=138
    期权Daily：https://tushare.pro/document/2?doc_id=159
    指数Daily：https://tushare.pro/document/2?doc_id=95
    数字货币：https://tushare.pro/document/41?doc_id=4

    #取000001的前复权行情
    df = ts.pro_bar(ts_code='000001.SZ', adj='qfq', start_date='20180101', end_date='20181011')
                ts_code     trade_date      open        high        low      close  \
    trade_date
    20181011    000001.SZ   20181011        1085.71     1097.59     1047.90  1065.19
    20181010    000001.SZ   20181010        1138.65     1151.61     1121.36  1128.92
    20181009    000001.SZ   20181009        1130.00     1155.93     1122.44  1140.81
    20181008    000001.SZ   20181008        1155.93     1165.65     1128.92  1128.92
    20180928    000001.SZ   20180928        1164.57     1217.51     1164.57  1193.74
    """
    token = config.get('token')
    pro = ts.pro_api(token=token, timeout=float(config.get('timeout')))
    start_date = config.get('start_date')
    end_date = config.get('end_date')
    if end_date == -1:
        end_date = datetime.datetime.today().strftime('%Y%m%d')
    df_all_bar_merge_mv = pd.DataFrame()
    for stock_code in code_list:
        emit_log(config, _Script, f"query data {stock_code} {code_list.index(stock_code)}/{len(code_list)}")
        bar_data = ts.pro_bar(ts_code=stock_code, api=pro, adj='qfq', start_date=start_date, end_date=end_date)
        # time.sleep(0.6)
        if bar_data is not None:    # e.g. 000003.SZ was particular transferred (PT), no bar
            bar_data = bar_data[['ts_code', 'trade_date', 'close', 'vol']]
            daily_basic_data = pro.daily_basic(ts_code=stock_code, start_date=start_date, end_date=end_date)[
                ['trade_date', 'total_mv']]
            df_single_stock_bar_merge_mv = pd.merge(bar_data, daily_basic_data, on='trade_date', how='left')
            df_all_bar_merge_mv = pd.concat([df_all_bar_merge_mv, df_single_stock_bar_merge_mv], ignore_index=True)

    return df_all_bar_merge_mv


@func_timer
def get_namechange_stock(code_list):
    """
    描述：历史名称变更记录

    输入参数：
    名称	    类型	必选	描述
    ts_code	    str	    N	    TS代码
    start_date	str	    N	    公告开始日期
    end_date	str	    N	    公告结束日期

    输出参数：
    名称	        类型	默认输出	    描述
    ts_code	        str	    Y	        TS代码
    name	        str	    Y	        证券名称
    start_date	    str	    Y	        开始日期
    end_date	    str	    Y	        结束日期
    ann_date	    str	    Y	        公告日期
    change_reason	str	    Y	        变更原因

        ts_code         name        start_date   end_date      change_reason
    0   600848.SH       上海临港    20151118      None              改名
    1   600848.SH       自仪股份    20070514      20151117         撤销ST
    2   600848.SH       ST自仪      20061026      20070513         完成股改
    3   600848.SH       SST自仪     20061009      20061025        未股改加S
    4   600848.SH       ST自仪      20010508      20061008         ST
    5   600848.SH       自仪股份    19940324      20010507         其他
    """
    token = config.get('token')
    pro = ts.pro_api(token=token, timeout=float(config.get('timeout')))
    df_namechange = pd.DataFrame()
    for code in code_list:
        namechange_data = pro.namechange(ts_code=code, start_date=config.get('start_date'), fields='')
        df_namechange = pd.concat([df_namechange, namechange_data], axis=0, ignore_index=True)
        time.sleep(0.6)  # maximum 100 request quotas per minute
    # df_stpt = df_namechange[df_namechange['name'].str.contains('ST')]

    return df_namechange


@func_timer
def main():
    emit_log(config, _Script, f"Program starts...")
    # concatenate listed, delisted, pending or company in other situations
    fields = "ts_code, symbol, name, area, industry, list_date, market, delist_date"
    df_stock_basic_overall = concat_stock_basic(fields)
    # print(df_stock_basic_overall)

    # save to csv file
    file_stock_basic_overall = f"stock_basic_overall.csv"
    save_dataframe(df_stock_basic_overall, file_stock_basic_overall)

    # list all stocks selected
    stock_code_list = df_stock_basic_overall['ts_code'].tolist()

    # # query back adjust bar data
    df_bar_mv = get_qfq_bar_data(stock_code_list)
    save_dataframe(df_bar_mv, f"stock_bar_marketcap.csv")

    # # find out st/pt stocks
    df_namechange = get_namechange_stock(stock_code_list)
    save_dataframe(df_namechange, f"stock_namechange.csv")
    emit_log(config, _Script, f"All finished.")


if __name__ == '__main__':
    main()
