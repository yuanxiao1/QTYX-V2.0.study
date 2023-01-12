#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

from urllib import request, parse
from datetime import datetime
import pandas as pd
import numpy as np
import random
import json
import re
import time
import sqlite3
import os
from pathlib import Path
from ApiData.Tushare import basic_code_list

# 爬虫取东方财富网沪深A股股票每日实时行情数据
class CrawerDailyData():

    pages = 11 # 目前A股的股票数量需要11页
    store_path = os.path.dirname(os.path.dirname(__file__)) + '/DataFiles/DailyData/'

    def __init__(self):

        self.filter = [u"最新价格", u"涨跌额", u"涨跌幅", u"成交量", u"成交额", u"振幅",
                       u"最高", u"最低", u"今开", u"昨收", u"量比", u"换手率", u"市盈率(动态)",
                       u"市净率", u"总市值", u"流通市值"]

        self.df_total = pd.DataFrame()  # 新建一个空的DataFrame
        self.cur_time = datetime.now().strftime("%Y-%m-%d")

    def get_header(self):

        # 构造请求头信息,随机抽取信息
        agent1 = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0'
        agent2 = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'
        agent3 = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'
        agent4 = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR ' \
                 '3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0) '
        agent5 = 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR ' \
                 '3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) '

        agent = random.choice([agent1, agent2, agent3, agent4, agent5])  # 请求头信息

        header = {
            'User-Agent': agent
        }
        return header


    def run(self):

        for page in range(1, self.pages):

            url = "http://75.push2.eastmoney.com/api/qt/clist/get?cb=jQuery1124006808348016960819_1607923077127" \
                  "&pn=" + str(
                page) + "&pz=500&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23" \
                        "&fields=f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18,f20,f21,f23&_=1607923077268"

            req_obj = request.Request(url, headers=self.get_header())
            resp = request.urlopen(req_obj).read().decode(encoding='utf-8')

            pattern = re.compile(r'"diff":\[(.*?)\]', re.S).findall(resp)
            st_data = pattern[0].replace("},{", "}walt{").split('walt')
            stocks = []

            for i in range(len(st_data)):

                stock = json.loads(st_data[i])

                stock_all = str(stock['f12']) + "," + str(stock['f14']) + "," + str(stock['f2']) + "," + str(
                    stock['f4']) + "," + \
                            str(stock['f3']) + "," + str(stock['f5']) + "," + str(stock['f6']) + "," + str(
                    stock['f7']) + "," + \
                            str(stock['f15']) + "," + str(stock['f16']) + "," + str(stock['f17']) + "," + str(
                    stock['f18']) + "," + \
                            str(stock['f10']) + "," + str(stock['f8']) + "," + str(stock['f9']) + "," + str(
                    stock['f23']) + "," + \
                            str(stock['f20']) + "," + str(stock['f21'])

                stocks.append(stock_all.split(","))

            df = pd.DataFrame(stocks, dtype=object)

            columns = {0: "股票代码", 1: "股票名称", 2: "最新价格", 3: "涨跌额", 4: "涨跌幅", 5: "成交量", 6: "成交额", 7: "振幅", 8: "最高", 9: "最低",
                       10: "今开", 11: "昨收", 12: "量比", 13: "换手率", 14: "市盈率(动态)", 15: "市净率", 16: "总市值", 17: "流通市值"}
            df.rename(columns=columns, inplace=True)

            self.df_total = pd.concat([self.df_total, df], ignore_index=True)

            time.sleep(0.5)

        self.df_total.replace("-", np.nan, inplace=True)

        self.df_total = self.df_total.astype({'最新价格': 'float64', '涨跌额': 'float64', '涨跌幅': 'float64',
                                              '成交量': 'float64', '成交额': 'float64', '振幅': 'float64',
                                              '最高': 'float64', '最低': 'float64', '今开': 'float64', '昨收': 'float64',
                                              '量比': 'float64', '换手率': 'float64', '市盈率(动态)': 'float64', '市净率': 'float64',
                                              '总市值': 'float64', '流通市值': 'float64'})

        self.df_total["股票代码"] = self.df_total["股票代码"].apply(lambda x: x+'.SH' if x[0]=='6' else x+'.SZ')

        return self.df_total

    def save_csv(self):

        file_exist = Path(self.store_path + u"A股每日指标-{0}.csv".format(self.cur_time))
        self.df_total.to_csv(file_exist, columns=self.df_total.columns, index=True, encoding='GBK')

    def save_db(self):

        file_exist = Path(self.store_path + u'stock-daily.db')
        conn = sqlite3.connect(file_exist)
        self.df_total.to_sql('A股每日指标-{0}'.format(self.cur_time), conn, index=False, if_exists='replace')

class CrawerDailyBackend(CrawerDailyData):

    def __init__(self, syslog_obj):

        CrawerDailyData.__init__(self)

        self.tran_col = {}
        self.filter = []
        self.syslog = syslog_obj

    def datafame_join(self, date_val):

        # 使用tushare pro的stock_basic和爬虫的daily接口合并

        self.syslog.re_print("开始获取爬虫每日行情基本面数据...\n")

        try:
            df_stbasic = basic_code_list(['ts_code','symbol','name','area','industry','list_date'])
            df_stbasic.rename(columns={"ts_code": "股票代码", "area": "所在地域", "industry": u"所属行业","list_date": u"上市日期"},
                              inplace=True)

        except:
            self.syslog.re_print("请检查tushare接口-[stock_basic]是否正常！\n")
            df_stbasic = pd.DataFrame()

        try:
            df_dybasic = self.run()
        except:
            self.syslog.re_print("请检查爬虫接口-[CrawerDailyData]是否正常！\n")

            df_dybasic = pd.DataFrame()

        self.save_csv()
        self.save_db()

        if (df_stbasic.empty != True) and (df_dybasic.empty != True): # 两个接口都正常是合并

            df_join = pd.merge(df_stbasic, df_dybasic, on='股票代码', left_index=False, right_index=False,
                         how='inner')
            #df_join.drop_duplicates(subset=['股票名称'], keep='first', inplace=True)
            df_join.drop(['symbol', 'name'], axis=1, inplace=True)

            self.syslog.re_print("爬虫每日行情基本面数据获取成功！\n")

        elif df_stbasic.empty != True: # 仅返回正常的接口
            df_join = df_stbasic

        elif df_dybasic.empty != True: # 仅返回正常的接口
            df_join = df_dybasic
        else:
            df_join = pd.DataFrame()

        return df_join

