#! /usr/bin/env python 
#-*- encoding: utf-8 -*- 
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import baostock as bs
import numpy as np
import pandas as pd
import sqlite3

def bs_k_data_stock(code_val='sz.000651', start_val='2009-01-01', end_val='2019-06-01',
                    freq_val='d', adjust_val='3'):

    # 登陆系统
    lg = bs.login()

    # 获取历史行情数据
    fields= "date,open,high,low,close,volume,pctChg"

    if (code_val.find('sz.399')!= -1) or (code_val.find('sh.000')!=-1):
        # 行业指数 无分钟线
        df_bs = bs.query_history_k_data_plus(code_val, fields, start_date=start_val, end_date=end_val,
                                             frequency=freq_val)

    else:
        # 个股指数
        if (freq_val != 'd') and (freq_val != 'w') and (freq_val != 'm'):
            fields = fields.replace('pctChg', 'time') # 分钟线无pctChg 但有time

        df_bs = bs.query_history_k_data_plus(code_val, fields, start_date=start_val, end_date=end_val,
                                             frequency=freq_val,
                                             adjustflag=adjust_val)  # <class 'baostock.data.resultset.ResultData'>

    # frequency="d"取日k线，adjustflag="3"默认不复权，1：后复权；2：前复权

    data_list = []

    while (df_bs.error_code == '0') & df_bs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(df_bs.get_row_data())

    result = pd.DataFrame(data_list, columns=df_bs.fields)
    result.replace("", 0, inplace=True)
    result = result.astype({'close': 'float64', 'open': 'float64', 'low': 'float64', 'high': 'float64'})

    result.volume = result.volume.astype('float64')
    result.volume = result.volume/100 # 单位转换：股-手

    if (freq_val == 'd') or (freq_val == 'w') or (freq_val == 'm'):

        result.pctChg = result.pctChg.astype('float64')

        result.date = pd.DatetimeIndex(result.date)
        result.set_index("date", drop=True, inplace=True)
        result.index = result.index.set_names('Date')

        recon_data = {'High': result.high, 'Low': result.low, 'Open': result.open, 'Close': result.close,\
                      'Volume': result.volume, 'pctChg': result.pctChg}
    else:
        result.time = result.time.apply(lambda x: x[:-4])
        result.time = pd.to_datetime(result.time, yearfirst=True, format='%Y%m%d%H%M%S')
        result.set_index("time", drop=True, inplace=True)
        result.index = result.index.set_names('Date')

        recon_data = {'High': result.high, 'Low': result.low, 'Open': result.open, 'Close': result.close, \
                      'Volume': result.volume}
    result.index = result.index.set_names('Date')
    df_recon = pd.DataFrame(recon_data)
    # 登出系统
    bs.logout()
    return df_recon

def bs_profit_data_stock(code_val='sh.600000', year_val='2017', quarter_val=2):

    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)

    # 查询季频估值指标盈利能力
    profit_list = []
    rs_profit = bs.query_profit_data(code=code_val, year=year_val, quarter=quarter_val)
    while (rs_profit.error_code == '0') & rs_profit.next():
        profit_list.append(rs_profit.get_row_data())
    result_profit = pd.DataFrame(profit_list, columns=rs_profit.fields)

    # 登出系统
    bs.logout()
    return result_profit


def bs_cash_flow_stock(code_val='sh.600000', year_val=2020, quarter_val=2):

    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)

    # 季频现金流量
    cash_flow_list = []
    rs_cash_flow = bs.query_cash_flow_data(code=code_val, year=year_val, quarter=quarter_val)
    while (rs_cash_flow.error_code == '0') & rs_cash_flow.next():
        cash_flow_list.append(rs_cash_flow.get_row_data())
    df_cash_flow = pd.DataFrame(cash_flow_list, columns=rs_cash_flow.fields)

    df_cash_flow.rename(columns = {"code": "股票代码",  "pubDate":"发布日期", "statDate":"统计截止日",
                                    # 季频现金流量
                                    "CAToAsset": "流动资产除以总资产", "NCAToAsset": "非流动资产除以总资产", "tangibleAssetToAsset": "有形资产除以总资产",
                                    "ebitToInterest": "已获利息倍数", "CFOToOR": "经营活动产生的现金流量净额除以营业收入",
                                    "CFOToNP": "经营性现金净流量除以净利润", "CFOToGr": "经营性现金净流量除以营业总收入",
                                    },  inplace=True)

    # 登出系统
    bs.logout(df_cash_flow)
    return df_cash_flow

