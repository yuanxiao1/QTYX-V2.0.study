#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究
import time
import datetime
import pandas as pd

from CommIf.SysFile import Base_File_Oper
from ApiData.Baostock import bs_k_data_stock, bs_cash_flow_stock
from StrategyGath.StrategyGath import Base_Strategy_Group
from ApiData.Csvdata import (
    Csv_Backend
)

class EventHandle:

    event_task = {}

    def __init__(self, *args, **kwargs):

        # ----- gui event -----

        self.event_task['get_stock_dat'] = self.get_stock_dat
        self.event_task['cfg_firm_para'] = self.cfg_firm_para
        self.event_task['cfg_back_para'] = self.cfg_back_para
        self.event_task['cfg_group_para'] = self.cfg_group_para
        self.event_task['get_csvst_dat'] = self.get_csvst_dat
        self.event_task['get_cash_flow'] = self.get_cash_flow
        self.event_task['get_csvst_pool'] = self.get_csvst_pool



    #### 配置股票数据相关 ####
    def get_stock_dat(self, **kwargs):
        # baostock接口获取行情数据
        baost_para = {"5分钟": "5", "60分钟": "60", "30分钟": "30", "日线": "d", "周线": "w",
                      "后复权": "1", "前复权": "2", "不复权": "3"}

        # 传递参数
        st_code = kwargs["st_code"]
        sdate_obj = kwargs["sdate_obj"]
        edate_obj = kwargs["edate_obj"]
        period_val = baost_para[kwargs["st_period"]]
        auth_val = baost_para[kwargs["st_auth"]]

        sdate_val = datetime.datetime(sdate_obj.year, sdate_obj.month + 1, sdate_obj.day)
        edate_val = datetime.datetime(edate_obj.year, edate_obj.month + 1, edate_obj.day)

        try:
            df = bs_k_data_stock(st_code,
                                 start_val=sdate_val.strftime('%Y-%m-%d'),
                                 end_val=edate_val.strftime('%Y-%m-%d'),
                                 freq_val=period_val,
                                 adjust_val=auth_val)
            # df.to_csv("offline-2021-12-29.csv", columns=df.columns, index=True, encoding='GB18030')
        except:
            df = pd.DataFrame()
            print("Baostock 获取异常， 等待10秒后重试！")
            time.sleep(10)
        finally:
            return df

    def get_csvst_dat(self, **kwargs):
        # csv文件获取行情数据

        # 传递参数
        get_path = kwargs["get_path"]
        sdate_obj = kwargs["sdate_obj"]
        edate_obj = kwargs["edate_obj"]
        adjust_val = kwargs["st_auth"]
        period_val = kwargs["st_period"]

        # 起始日期和结束日期
        sdate_val = datetime.datetime(sdate_obj.year, sdate_obj.month + 1, sdate_obj.day)
        edate_val = datetime.datetime(edate_obj.year, edate_obj.month + 1, edate_obj.day)

        try:
            # 时间格式'%Y-%m-%d %H:%M'能够过滤'%Y-%m-%d'
            df = Csv_Backend.load_stock_data(get_path, sdate_val, edate_val, adjust_val, period_val)
        except:
            df = pd.DataFrame()
        finally:
            # 返回数据
            return df

    def get_csvst_pool(self, **kwargs):
        # csv文件加载股票池

        # 代码格式转换
        def f(x):
            if x.find('.') != -1:
                if x.find(".") == 6: # 匹配xxxxxx.SH 或 .SZ
                    num, sym = x.lower().split('.')
                    code = sym + "." + num
                else:
                    code = x
            else:
                if x[0] == '6':
                    code = "sh." + x
                else:
                    code = "sz." + x
            print(code)
            return code

        # 传递参数
        get_path = kwargs["get_path"]
        try:
            csv_df = pd.read_csv(get_path, parse_dates=True, index_col=0, encoding='gbk', engine='python')
            csv_df['股票代码'] = csv_df['股票代码'].apply(f)
            st_name_code_dict = dict(zip(csv_df["股票名称"].values, csv_df["股票代码"].values))
        except:
            st_name_code_dict = {}
        finally:
            # 返回数据
            return st_name_code_dict

    def get_cash_flow(self, **kwargs):
        # 获取 现金流量表 风险预警

        # 传递参数
        st_code = kwargs["st_code"]

        # 计算当前季度
        cur_year = datetime.datetime.now().year
        cur_quarter = (datetime.datetime.now().month - 1) // 3 + 1 # 向下取整数

        if cur_quarter == 1:
            pre_fst_year = cur_year - 1
            pre_fst_quarter = 4
        else:
            pre_fst_year = cur_year
            pre_fst_quarter = cur_quarter - 1

        if pre_fst_quarter == 1:
            pre_sec_year = pre_fst_year - 1
            pre_sec_quarter = 4
        else:
            pre_sec_year = pre_fst_year
            pre_sec_quarter = pre_fst_quarter - 1

        try:
            # 因为公告发布延迟 获取上季度的现金流量数据
            df = bs_cash_flow_stock(st_code, pre_fst_year, pre_fst_quarter)
            if df.empty == True:
                # 获取上上一季度的现金流量数据
                df = bs_cash_flow_stock(st_code, pre_sec_year, pre_sec_quarter)
        except:
            df = pd.DataFrame()

        if df.empty != True:

            text = "发布日期:%s\n统计截止日:%s\n经营活动产生的现金流量净额除以营业收入:%s\n经营性现金净流量除以净利润:%s\n经营性现金净流量除以营业总收入:%s\n" \
                   %(df["发布日期"][0], df["统计截止日"][0], df["经营活动产生的现金流量净额除以营业收入"][0],
                    df["经营性现金净流量除以净利润"][0], df["经营性现金净流量除以营业总收入"][0])

            if (float(df["经营活动产生的现金流量净额除以营业收入"][0]) < 0)or(float(df["经营性现金净流量除以净利润"][0]) < 0)\
                or(float(df["经营性现金净流量除以营业总收入"][0]) < 0):
                text += "\n公司现金流量存在较大风险！\n"
            else:
                text += "\n公司现金流量正常......\n"
        else:
            text = ''
        return text


    #### 配置文件获取相关 ####
    def cfg_firm_para(self, **kwargs):
        # 行情显示界面 配置文件

        # 传递参数
        st_code = kwargs["st_code"]
        st_name = kwargs["st_name"]
        st_auth = kwargs["st_auth"]
        st_period = kwargs["st_period"]

        # 加载参数
        firm_para = Base_File_Oper.load_sys_para("firm_para.json")

        # 更新参数
        firm_para['subplots_dict']['graph_fst']['title'] = st_code+'/'+st_name+'/'+st_period+'/'+st_auth

        if "st_label" in kwargs.keys():
            # 适应于衍生技术指标的显示
            st_label = kwargs["st_label"]
            firm_para['subplots_dict']['graph_fst']['graph_type'][st_label] = 'null'

        # 返回参数
        return firm_para['subplots_dict']


    def cfg_group_para(self, **kwargs):
        # 股票组合分析显示界面 配置文件

        # 传递参数
        st_code = kwargs["st_code"]
        st_auth = kwargs["st_auth"]
        st_period = kwargs["st_period"]

        # 加载参数
        group_para = Base_File_Oper.load_sys_para("group_para.json")

        # 更新参数
        group_para['subplots_dict']['graph_fst']['title'] = st_code+' '+st_period+' '+st_auth

        # 返回参数
        return group_para


    def cfg_back_para(self, **kwargs):
        # 回测显示界面 配置文件

        # 传递参数
        st_code = kwargs["st_code"]
        cash_value = kwargs["cash_value"]
        slippage_value = kwargs["slippage_value"]
        commission_value = kwargs["commission_value"]
        tax_value = kwargs["tax_value"]
        stake_value = kwargs["stake_value"]

        # 加载参数
        back_para = Base_File_Oper.load_sys_para("back_para.json")
        # 更新回测参数
        back_para['subplots_dict']['graph_sec']['graph_type']['cash_profit']['cash_hold'] = cash_value
        back_para['subplots_dict']['graph_sec']['graph_type']['cash_profit']['slippage'] = slippage_value
        back_para['subplots_dict']['graph_sec']['graph_type']['cash_profit']['c_rate'] = commission_value
        back_para['subplots_dict']['graph_sec']['graph_type']['cash_profit']['t_rate'] = tax_value
        back_para['subplots_dict']['graph_sec']['graph_type']['cash_profit']['stake_size'] = stake_value
        back_para['subplots_dict']['graph_fst']['title'] = st_code + "-回测分析"
        # 保存参数
        Base_File_Oper.save_sys_para("back_para.json", back_para)
        # 返回参数
        return back_para['subplots_dict']

    def cfg_sub_para(self, **kwargs):

        # 传递参数
        st_code = kwargs["st_code"]
        st_auth = kwargs["st_auth"]
        st_period = kwargs["st_period"]

        sub_para = Base_File_Oper.load_sys_para("sub_para.json")
        sub_para['subplots_dict']['graph_fst']['title'] = st_code+' '+st_period+' '+st_auth

        return sub_para['subplots_dict']

    def call_method( self, f, **kwargs):

        return f(**kwargs)

