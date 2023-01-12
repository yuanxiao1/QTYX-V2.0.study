#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import numpy as np
import talib

from MultiGraphs.BaseGraphs import MplTypesDraw, DefTypesPool
from MultiGraphs.SignalOutput import CurHaveSig

# 属于<8.1 定制可视化接口>的实现
class MarketGraphIf(MplTypesDraw, CurHaveSig):

    app = DefTypesPool()
    ##########################行情分析界面###############################

    ##### 基础指标
    # 参考<8.2.1 原生量价指标可视化>
    @app.route_types(u"ochl")
    def ochl_graph(stock_dat, sub_graph, df_dat=None):  # prepare data
        type_dict = {'Open': stock_dat.Open,
                     'Close': stock_dat.Close,
                     'High': stock_dat.High,
                     'Low': stock_dat.Low
                     }
        view_function = MplTypesDraw.mpl.route_output(u"ochl")
        view_function(stock_dat.index, type_dict, sub_graph)

    # 参考<8.2.1 原生量价指标可视化>
    @app.route_types(u"vol")
    def vol_graph(stock_dat, sub_graph, df_dat=None):  # prepare data

        type_dict = {'bar_red': np.where(stock_dat.Open < stock_dat.Close, stock_dat.Volume, 0), # 绘制BAR>0 柱状图
                     'bar_green': np.where(stock_dat.Open > stock_dat.Close, stock_dat.Volume, 0) # 绘制BAR<0 柱状图
                     }

        view_function = MplTypesDraw.mpl.route_output(u"bar")
        view_function(stock_dat.index, type_dict, sub_graph)

    # 参考<8.2.2 移动平均线 SMA 可视化>
    @app.route_types(u"sma")
    def sma_graph(stock_dat, sub_graph, periods):  # prepare data
        for val in periods:
            type_dict = {'SMA'+str(val): stock_dat.Close.rolling(window=val).mean()}

            view_function = MplTypesDraw.mpl.route_output(u"line")
            view_function(stock_dat.index, type_dict, sub_graph)

    # 参考<8.2.4 趋势类指标 MACD 可视化>
    @app.route_types(u"macd")
    def macd_graph(stock_dat, sub_graph, df_dat=None):  # prepare data

        macd_dif = stock_dat['Close'].ewm(span=12, adjust=False).mean() - stock_dat['Close'].ewm(span=26,                                                                                         adjust=False).mean()
        macd_dea = macd_dif.ewm(span=9, adjust=False).mean()
        macd_bar = 2 * (macd_dif - macd_dea)

        type_dict = {'bar_red': np.where(macd_bar > 0, macd_bar, 0),  # 绘制BAR>0 柱状图
                     'bar_green': np.where(macd_bar < 0, macd_bar, 0)  # 绘制BAR<0 柱状图
                     }
        view_function = MplTypesDraw.mpl.route_output(u"bar")
        view_function(stock_dat.index, type_dict, sub_graph)

        type_dict = {'macd dif': macd_dif,
                     'macd dea': macd_dea
                     }
        view_function = MplTypesDraw.mpl.route_output(u"line")
        view_function(stock_dat.index, type_dict, sub_graph)

    # 参考<8.2.3 震荡类指标 KDJ 可视化>
    @app.route_types(u"kdj")
    def kdj_graph(stock_dat, sub_graph, df_dat=None):  # prepare data

        low_list = stock_dat['Low'].rolling(9, min_periods=1).min()
        high_list = stock_dat['High'].rolling(9, min_periods=1).max()
        rsv = (stock_dat['Close'] - low_list) / (high_list - low_list) * 100
        stock_dat['K'] = rsv.ewm(com=2, adjust=False).mean()
        stock_dat['D'] = stock_dat['K'].ewm(com=2, adjust=False).mean()
        stock_dat['J'] = 3 * stock_dat['K'] - 2 * stock_dat['D']

        type_dict = {'K': stock_dat.K,
                     'D': stock_dat.D,
                     'J': stock_dat.J
                    }
        view_function = MplTypesDraw.mpl.route_output(u"line")
        view_function(stock_dat.index, type_dict, sub_graph)

    ##### 衍生指标
    # 参考<8.3.1 均线交叉信号可视化>
    @app.route_types(u"cross")
    def cross_graph(stock_dat, sub_graph, df_dat=None):  # prepare data

        # 绘制移动平均线图
        stock_dat["short_list"] = stock_dat['Close'].rolling(window=20).mean()  # pd.rolling_mean(stock_dat.Close,window=20)
        stock_dat["long_list"] = stock_dat['Close'].rolling(window=30).mean()  # pd.rolling_mean(stock_dat.Close,window=30)

        # 长短期均线序列相减取符号
        list_diff = np.sign(stock_dat["short_list"] - stock_dat["long_list"])
        list_signal = np.sign(list_diff - list_diff.shift(1))

        down_cross = stock_dat[list_signal < 0]
        up_cross = stock_dat[list_signal > 0]

        type_dict = {'death':
                         {
                            'andata': down_cross,
                            'va': 'top',
                            'xy_y': 'short_list',
                            'xytext': (0, +20), # 提示位置偏移
                            'fontsize': 8,
                            'arrow': dict(facecolor='green', shrink=0.1)
                         },
                     'gold':
                         {
                             'andata': up_cross,
                             'va': 'bottom',
                             'xy_y': 'long_list',
                             'xytext': (0, -20), # 提示位置偏移
                             'fontsize': 8,
                             'arrow': dict(facecolor='red', shrink=0.1)
                         }
                     }
        view_function = MplTypesDraw.mpl.route_output(u"annotate")
        view_function(stock_dat.index, type_dict, sub_graph)

    # 参考<8.3.2 股价跳空缺口可视化>
    def apply_gap(changeRatio, preLow, preHigh, Low, High, threshold):
        jump_power = 0
        if (changeRatio > 0) and ((Low - preHigh) > threshold):
            # 向上跳空 (今最低-昨最高)/阈值
            jump_power = (Low - preHigh) / threshold  # 正数
        elif (changeRatio < 0) and ((preLow - High) > threshold):
            # 向下跳空 (今最高-昨最低)/阈值
            jump_power = (High - preLow) / threshold  # 负数
        return jump_power

    # 参考<8.3.2 股价跳空缺口可视化>
    @app.route_types(u"jump")
    def jump_graph(stock_dat, sub_graph, df_dat=None):  # prepare data

        # 挖掘跳空缺口
        jump_threshold = stock_dat.Close.median() * 0.01  # 跳空阈值 收盘价中位数*0.01
        stock_dat['changeRatio'] = stock_dat.Close.pct_change() * 100  # 计算涨/跌幅 (今收-昨收)/昨收*100% 判断向上跳空缺口/向下跳空缺口
        stock_dat['preLow'] = stock_dat.Low.shift(1)  # 增加昨日最低价序列
        stock_dat['preHigh'] = stock_dat.High.shift(1)  # 增加昨日最高价序列
        stock_dat = stock_dat.assign(jump_power=0)

        # for kl_index in np.arange(0, df_stockload.shape[0]):
        #    today = df_stockload.iloc[kl_index]
        # note: A value is trying to be set on a copy of a slice from a DataFrame
        # involve change the value of df_stockload but iloc just copy the dataframe

        stock_dat['jump_power'] = stock_dat.apply(lambda row: MarketGraphIf.apply_gap(row['changeRatio'],
                                                                        row['preLow'],
                                                                        row['preHigh'],
                                                                        row['Low'],
                                                                        row['High'],
                                                                        jump_threshold), axis=1)
        up_jump = stock_dat[(stock_dat.changeRatio > 0) & (stock_dat.jump_power > 0)]
        down_jump = stock_dat[(stock_dat.changeRatio < 0) & (stock_dat.jump_power < 0)]

        type_dict = {'up':
                         {
                            'andata': up_jump,
                             'va': 'top',
                             'xy_y': 'preHigh',
                             'xytext': (0, -20), # 提示位置偏移
                             'fontsize': 8,
                             'arrow': dict(facecolor='red', shrink=0.1)
                         },
                     'down':
                         {
                             'andata': down_jump,
                             'va': 'bottom',
                             'xy_y': 'preLow',
                             'xytext': (0, 20), # 提示位置偏移
                             'fontsize': 8,
                             'arrow': dict(facecolor='green', shrink=0.1)
                         }
                     }

        print(up_jump.filter(['jump_power', 'preClose', 'changeRatio', 'Close', 'Volume']))  # 向上跳空缺口 按顺序显示列
        """
                    jump_power  changeRatio  Close    Volume
        Date                                                
        2018-10-22        1.07         3.83  40.11  8.51e+07
        2019-01-09        1.58         3.22  37.51  1.06e+08
        2019-04-09       11.48        10.00  51.93  1.08e+07
        2019-04-10        6.40         9.99  57.12  3.23e+08
        """
        print(down_jump.filter(['jump_power', 'preClose', 'changeRatio', 'Close', 'Volume']))  # 向下跳空缺口 按顺序显示列
        """
                    jump_power  changeRatio  Close    Volume
        Date                                                
        2018-10-08       -1.22        -5.65  37.93  7.15e+07
        """

        format = lambda x: '%.2f' % x
        up_jump = up_jump[(np.abs(up_jump.changeRatio) > 2) & (up_jump.Volume > up_jump.Volume.median())]  # abs取绝对值
        up_jump = up_jump.applymap(format)  # 处理后数据为str
        print(up_jump.filter(['jump_power', 'preClose', 'changeRatio', 'Close', 'Volume']))  # 按顺序只显示该列
        """
                   jump_power changeRatio  Close        Volume
        Date                                                  
        2019-01-09       1.58        3.22  37.51  105806077.00
        2019-04-10       6.40        9.99  57.12  322875034.00
        """
        down_jump = down_jump[
            (np.abs(down_jump.changeRatio) > 2) & (down_jump.Volume > down_jump.Volume.median())]  # abs取绝对值
        down_jump = down_jump.applymap(format)  # 处理后数据为str
        print(down_jump.filter(['jump_power', 'preClose', 'changeRatio', 'Close', 'Volume']))  # 按顺序只显示该列
        """
        Empty DataFrame
        Columns: [jump_power, changeRatio, Close, Volume]
        Index: []
        """
        view_function = MplTypesDraw.mpl.route_output(u"annotate")
        view_function(stock_dat.index, type_dict, sub_graph)

    # 8.3.4 黄金分割与支撑/阻力线
    @app.route_types(u"fibonacci")
    def fibonacci_graph(stock_dat, sub_graph, df_dat=None):  # prepare data
        # 绘制黄金分割线

        Fib_max = stock_dat.Close.max()
        Fib_maxid = stock_dat.index.get_loc(stock_dat.Close.idxmax())
        Fib_min = stock_dat.Close.min()
        Fib_minid = stock_dat.index.get_loc(stock_dat.Close.idxmin())
        Fib_382 = (Fib_max - Fib_min) * 0.382 + Fib_min
        Fib_618 = (Fib_max - Fib_min) * 0.618 + Fib_min
        print(u'黄金分割0.382：{}'.format(round(Fib_382, 2)))
        print(u'黄金分割0.618：{}'.format(round(Fib_618, 2)))
        # 黄金分割0.382：46.88
        # 黄金分割0.618：53.8

        max_df = stock_dat[stock_dat.Close == stock_dat.Close.max()]
        min_df = stock_dat[stock_dat.Close == stock_dat.Close.min()]
        print(max_df)
        print(min_df)

        # graph_kline.legend(['0.382', '0.618'], loc='upper left')
        type_dict = {'Fib_382':
                             {'pos': Fib_382,
                              'c': 'r'
                              },
                    'Fib_618':
                             {'pos': Fib_618,
                              'c': 'g'
                              }
                    }
        view_function = MplTypesDraw.mpl.route_output(u"hline")
        view_function(stock_dat.index, type_dict, sub_graph)


    ##### K线形态指标
    # 参考<8.4.2 常见 K 线形态的识别方法>
    @app.route_types(u"CDLDARKCLOUDCOVER")
    def dark_cloud_cover_graph(stock_dat, sub_graph, df_dat=None):  # prepare data
        # 绘制 talib K线形态 乌云压顶
        CDLDARKCLOUDCOVER = talib.CDLDARKCLOUDCOVER(stock_dat.Open.values, stock_dat.High.values, stock_dat.Low.values,
                                                    stock_dat.Close.values)

        pattern = stock_dat[(CDLDARKCLOUDCOVER == 100) | (CDLDARKCLOUDCOVER == -100)]

        type_dict = {u'CDLDARKCLOUDCOVER':
                              {'andata': pattern,
                               'va': 'bottom',
                               'xy_y': 'High',
                               'xytext': (0, 20), # 提示位置偏移
                               'fontsize': 8,
                               'arrow': dict(arrowstyle='->', facecolor='blue',
                                             connectionstyle="arc3,rad=.2")
                               }
                    }
        view_function = MplTypesDraw.mpl.route_output(u"annotate")
        view_function(stock_dat.index, type_dict, sub_graph)


    @app.route_types(u"CDL3BLACKCROWS")
    def balck3_crows_graph(stock_dat, sub_graph, df_dat=None):  # prepare data
        # 绘制 talib K线形态 三只乌鸦
        CDL3BLACKCROWS = talib.CDL3BLACKCROWS(stock_dat.Open.values, stock_dat.High.values, stock_dat.Low.values,
                                                    stock_dat.Close.values)

        pattern = stock_dat[(CDL3BLACKCROWS == 100) | (CDL3BLACKCROWS == -100)]

        type_dict = {u'CDL3BLACKCROWS':
                              {'andata': pattern,
                               'va': 'bottom',
                               'xy_y': 'High',
                               'xytext': (0, 20), # 提示位置偏移
                               'fontsize': 8,
                               'arrow': dict(arrowstyle='->', facecolor='blue',
                                             connectionstyle="arc3,rad=.2")
                               }
                    }
        view_function = MplTypesDraw.mpl.route_output(u"annotate")
        view_function(stock_dat.index, type_dict, sub_graph)


    # 参考<8.4.2 常见 K 线形态的识别方法>
    @app.route_types(u"CDLDOJISTAR")
    def do_jistar_graph(stock_dat, sub_graph, df_dat=None):  # prepare data
        # 绘制 talib K线形态 十字星
        CDLDOJISTAR = talib.CDLDOJISTAR(stock_dat.Open.values, stock_dat.High.values, stock_dat.Low.values,
                                                    stock_dat.Close.values)

        pattern = stock_dat[(CDLDOJISTAR == 100) | (CDLDOJISTAR == -100)]

        type_dict = {u'CDLDOJISTAR':
                              {'andata': pattern,
                               'va': 'bottom',
                               'xy_y': 'High',
                               'xytext': (0, 20), # 提示位置偏移
                               'fontsize': 8,
                               'arrow': dict(arrowstyle='->', facecolor='blue',
                                             connectionstyle="arc3,rad=.2")
                               }
                    }
        view_function = MplTypesDraw.mpl.route_output(u"annotate")
        view_function(stock_dat.index, type_dict, sub_graph)

    # 参考<8.4.2 常见 K 线形态的识别方法>
    @app.route_types(u"CDLHAMMER")
    def hammer_graph(stock_dat, sub_graph, df_dat=None):  # prepare data
        # 绘制 talib K线形态 锤头
        CDLHAMMER = talib.CDLHAMMER(stock_dat.Open.values, stock_dat.High.values, stock_dat.Low.values,
                                                    stock_dat.Close.values)

        pattern = stock_dat[(CDLHAMMER == 100) | (CDLHAMMER == -100)]

        type_dict = {u'CDLHAMMER':
                              {'andata': pattern,
                               'va': 'bottom',
                               'xy_y': 'High',
                               'xytext': (0, 20), # 提示位置偏移
                               'fontsize': 8,
                               'arrow': dict(arrowstyle='->', facecolor='blue',
                                             connectionstyle="arc3,rad=.2")
                               }
                    }
        view_function = MplTypesDraw.mpl.route_output(u"annotate")
        view_function(stock_dat.index, type_dict, sub_graph)

    # 参考<8.4.2 常见 K 线形态的识别方法>
    @app.route_types(u"CDLSHOOTINGSTAR")
    def shooting_star_graph(stock_dat, sub_graph, df_dat=None):  # prepare data
        # 绘制 talib K线形态 射击之星
        CDLSHOOTINGSTAR = talib.CDLSHOOTINGSTAR(stock_dat.Open.values, stock_dat.High.values, stock_dat.Low.values,
                                                    stock_dat.Close.values)

        pattern = stock_dat[(CDLSHOOTINGSTAR == 100) | (CDLSHOOTINGSTAR == -100)]

        type_dict = {u'CDLSHOOTINGSTAR':
                              {'andata': pattern,
                               'va': 'bottom',
                               'xy_y': 'High',
                               'xytext': (0, 20), # 提示位置偏移
                               'fontsize': 8,
                               'arrow': dict(arrowstyle='->', facecolor='blue',
                                             connectionstyle="arc3,rad=.2")
                               }
                    }
        view_function = MplTypesDraw.mpl.route_output(u"annotate")
        view_function(stock_dat.index, type_dict, sub_graph)




