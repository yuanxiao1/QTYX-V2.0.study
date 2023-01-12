#! /usr/bin/env python 
#-*- encoding: utf-8 -*- 
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import json
import pandas as pd
import os

class Base_File_Oper():

    rel_path = os.path.dirname(os.path.dirname(__file__)) + '/ConfigFiles/'

    @staticmethod
    def load_sys_para(filename):
        with open(Base_File_Oper.rel_path + filename, 'r', encoding='utf-8') as load_f:
            para_dict = json.load(load_f)
        return para_dict

    @staticmethod
    def save_sys_para(filename, para_dict):
        with open(Base_File_Oper.rel_path + filename, "w", encoding='utf-8') as save_f:
            json.dump(para_dict, save_f, ensure_ascii=False, indent=4)

    @staticmethod
    def load_tushare_basic():
        # 加载tushare basic接口的本地数据
        df_basic = pd.read_csv(Base_File_Oper.rel_path + "tushare_basic_info.csv", parse_dates=True, index_col=0, encoding='GBK')
        return df_basic

    @staticmethod
    def save_tushare_basic(df_basic):
        # 存储tushare basic接口的本地数据
        df_basic.to_csv(Base_File_Oper.rel_path + "tushare_basic_info.csv", columns=df_basic.columns, index=True, encoding='GBK')

    @staticmethod
    def read_tushare_token():
        # 设置token
        with open(Base_File_Oper.rel_path + 'token.txt', 'r', encoding='utf-8') as f:
            token = f.read()  # 读取你的token
        return token

    @staticmethod
    def save_patten_analysis(df_basic, filename):
        # 存储形态识别分析结果
        df_basic.to_csv(Base_File_Oper.rel_path + filename +".csv", columns=df_basic.columns, index=True, encoding='GBK')

    @staticmethod
    def read_log_trade():
        with open(Base_File_Oper.rel_path + 'logtrade.txt', 'r', encoding='gbk') as f:
            info = f.read()
        return info

