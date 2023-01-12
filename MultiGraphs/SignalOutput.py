#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import numpy as np
from CommIf.DefPool import DefTypesPool

class CurHaveSig():

    ind = DefTypesPool()

    @ind.route_types(u"cross")
    def corss_detect(stock_dat):
        # 检测当前是否有交叉信号

        # 绘制移动平均线图
        stock_dat["short_list"] = stock_dat['Close'].rolling(window=20).mean()  # pd.rolling_mean(stock_dat.Close,window=20)
        stock_dat["long_list"] = stock_dat['Close'].rolling(window=30).mean()  # pd.rolling_mean(stock_dat.Close,window=30)

        # 长短期均线序列相减取符号
        stock_dat["list_diff"] = np.sign(stock_dat["short_list"] - stock_dat["long_list"])
        stock_dat["list_signal"] = np.sign(stock_dat["list_diff"] - stock_dat["list_diff"].shift(1))

        curtime = stock_dat.index[-1].strftime("%Y-%m-%d")
        """
        down_cross = stock_dat[stock_dat["list_signal"] < 0]
        up_cross = stock_dat[stock_dat["list_signal"] > 0]
        """

        if stock_dat.loc[stock_dat.index[-1], "list_signal"] < 0:
            cont = f"当前时间 {curtime} 出现死叉!!!， "
        else:
            cont = f"当前时间 {curtime} 无死叉， "

        if stock_dat.loc[stock_dat.index[-1], "list_signal"] > 0:
            cont += f"出现金叉!!!"
        else:
            cont += f"无金叉"

        return cont+"\n"
