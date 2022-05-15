#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec#分割子图

from MultiGraphs.BaseGraphs import DefTypesPool, MplTypesDraw


class BacktsGraphIf(MplTypesDraw):

    app = DefTypesPool()

    def __init__(self, **kwargs):
        MplTypesDraw.__init__(self)

        self.fig = plt.figure(figsize=kwargs['figsize'], dpi=100, facecolor="white")#创建fig对象
        self.graph_dict = {}
        self.graph_curr = []

        try:
            gs = gridspec.GridSpec(kwargs['nrows'], kwargs['ncols'],
                                   left = kwargs['left'], bottom = kwargs['bottom'], right = kwargs['right'], top = kwargs['top'],
                                   wspace = kwargs['wspace'], hspace = kwargs['hspace'], height_ratios = kwargs['height_ratios'])
        except:
            raise Exception("para error")
        else:
            for i in range(0, kwargs['nrows'], 1):
                self.graph_dict[kwargs['subplots'][i]] = self.fig.add_subplot(gs[i, :])

    ##########################回测分析界面###############################

    # 参照<9.1.5 度量策略的最大风险回撤>
    @app.route_types(u"cash_profit")# cash profit and retracement
    def cash_profit_graph(stock_dat, sub_graph, para_dat = None):

        # 回测参数 由GUI配置
        cash_hold = float(para_dat["cash_hold"]) # cash_hold = 100000
        slippage = float(para_dat["slippage"]) # slippage = 0.01
        c_rate = float(para_dat["c_rate"]) # c_rate = 5.0 / 10000
        t_rate = float(para_dat["t_rate"]) # t_rate = 1.0 / 1000
        stake_size = para_dat["stake_size"] # 买入规模

        posit_num = 0  # 持股数目
        skip_days = False  # 持股/持币状态

        buy_price = 0 # 买入价格-含滑点
        sell_price = 0 # 卖出价格-含滑点

        win_count = 0 # 统计盈利次数
        loss_count = 0 # 统计亏损次数
        win_profit = 0 # 统计盈利幅值
        loss_profit = 0 # 统计亏损幅值

        # 最大风险回撤——资金最大回撤
        # 绝对收益—资金的度量
        for kl_index, today in stock_dat.iterrows():
            # 买入/卖出执行代码
            if today.Signal == 1 and skip_days == False:  # 买入
                buy_price = today.Close + slippage
                if stake_size == 'all': # 全仓买入
                    posit_num = int(cash_hold / (buy_price))  # 资金转化为股票
                    posit_num = int(posit_num / 100) * 100  # 买入股票最少100股，对posit_num向下取整百
                else: # 定额买入
                    posit_num = int(stake_size)

                buy_cash = posit_num * (buy_price)  # 计算买入股票所需现金
                # 计算手续费，不足5元按5元收，并保留2位小数
                commission = round(max(buy_cash * c_rate, 5), 2)

                if cash_hold > buy_cash - commission :
                    cash_hold = cash_hold - buy_cash - commission
                    skip_days = True # 买入成功
                    print(u"买入时间:{0}; 买入价格:{1}; 买入数量:{2}股; 手续费:{3}元".
                          format(kl_index.strftime("%y-%m-%d"), np.round(buy_price, 2), posit_num, commission))
                else:
                    print("当前时间:{0}; 您当前的资金不足以买入{1}股".format(kl_index.strftime("%y-%m-%d"), posit_num))


            elif today.Signal == -1 and skip_days == True:  # 卖出 避免未买先卖
                skip_days = False
                sell_price = today.Close - slippage
                sell_cash = posit_num * (sell_price) # 计算卖出股票得到的现金 卖出股票可以不是整百。
                # 计算手续费，不足5元按5元收，并保留2位小数
                commission = round(max(sell_cash * c_rate, 5), 2)
                # 计算印花税，保留2位小数
                tax = round(sell_cash * t_rate, 2)
                cash_hold = cash_hold + sell_cash - commission - tax # 剩余现金

                print(u"卖出时间:{0}; 买出价格:{1}; 卖出数量:{2}股; 手续费:{3}元, 印花税:{4}元".
                      format(kl_index.strftime("%y-%m-%d"), np.round(sell_price, 2), posit_num, commission, tax))

                pct_profit = np.round((sell_price - buy_price) / buy_price * 100, 2)
                print(u"交易价差:{0}; 交易涨幅:{1}".
                      format(np.round(sell_price - buy_price, 2), pct_profit))

                if sell_price > buy_price:
                    win_count = win_count + 1
                    win_profit = win_profit + pct_profit
                else:
                    loss_count = loss_count + 1
                    loss_profit = loss_profit + pct_profit

            if skip_days == True:  # 持股
                stock_dat.loc[kl_index, 'total'] = posit_num * today.Close + cash_hold
            else:  # 空仓
                stock_dat.loc[kl_index, 'total'] = cash_hold

            # expanding()计算资金曲线当前的滚动最高值
            stock_dat['max_total'] = stock_dat['total'].expanding().max()
            # 计算资金曲线在滚动最高值之后所回撤的百分比
            stock_dat['per_total'] = stock_dat['total'] / stock_dat['max_total']

        if loss_count == 0:
            print(f'亏损次数:{loss_count}, 盈利次数:{win_count}, 胜率:{round(win_count / (win_count + loss_count) * 100, 2)}%')
            print(f'平均亏损:{0}% 平均盈利:{round((win_profit / win_count), 2)}%')
        elif win_count == 0:
            print(f'亏损次数:{loss_count}, 盈利次数:{win_count}, 胜率:{round(win_count / (win_count + loss_count)*100, 2)}%')
            print(f'平均亏损:{round((loss_profit / loss_count), 2)}% 平均盈利:{0}%')
        else:
            print(f'亏损次数:{loss_count}, 盈利次数:{win_count}, 胜率:{round(win_count / (win_count + loss_count)*100, 2)}%')
            print(f'平均亏损:{round((loss_profit / loss_count), 2)}% 平均盈利:{round((win_profit / win_count), 2)}%')

        min_point_df = stock_dat.sort_values(by=['per_total'])[0:1]
        min_point_total = min_point_df.per_total
        max_point_df = stock_dat[stock_dat.index <= min_point_total.index[0]].sort_values(by=['total'],
                                                                                          ascending=False)[0:1]
        max_point_total = max_point_df.total
        # min_point_total = stock_dat.sort_values(by=['per_total']).iloc[[0], stock_dat.columns.get_loc('per_total')]
        # max_point_total = stock_dat[stock_dat.index <= min_point_total.index[0]].sort_values \
        #    (by=['total'], ascending=False).iloc[[0], stock_dat.columns.get_loc('total')]

        print("资金最大回撤%5.2f%% 从%s开始至%s结束" % ((1 - min_point_total.values) * 100, \
                                            max_point_total.index[0], min_point_total.index[0]))
        # 最大资金回撤 7.53%从2018-07-13 00:00:00开始至2018-09-12 00:00:00结束

        line_total = "资金总体收益%d；上涨幅度 %.2f%%" % (stock_dat['total'][-1], (stock_dat['total'][-1] - 100000) / 100000 * 100)
        print(line_total)
        max_total = "资金滚动最高值"

        type_dict = {line_total: stock_dat.total,
                     max_total: stock_dat.max_total,
                     }
        view_function = MplTypesDraw.mpl.route_output(u"line")
        view_function(stock_dat.index, type_dict, sub_graph)

        type_dict = {u"资金最大回撤\n{}".format(1 - min_point_total.values):
                         {'andata': min_point_df,
                          'va': 'top',
                          'xy_y': 'total',
                          'xytext': (0,stock_dat['High'].mean()),
                          'fontsize': 8,
                          'arrow': dict(facecolor='green', shrink=0.1)
                          },
                      }
        view_function = MplTypesDraw.mpl.route_output(u"annotate")
        view_function(stock_dat.index, type_dict, sub_graph)

    # 参照<9.1.4 度量策略与基准的相对收益>
    @app.route_types(u"cmp_profit")  # relative_profit
    def cmp_profit_graph(stock_dat, sub_graph, para_dat):

        # 相对收益—策略VS基准
        stock_dat['benchmark_profit_log'] = np.log(stock_dat.Close / stock_dat.Close.shift(1))
        stock_dat.loc[stock_dat.Signal == -1, 'Signal'] = 0
        stock_dat['trend_profit_log'] = stock_dat['Signal'] * stock_dat.benchmark_profit_log
        line_trend_key = "策略收益%.2f" % stock_dat['trend_profit_log'].cumsum()[-1]
        line_bench_key = "基准收益%.2f" % stock_dat['benchmark_profit_log'].cumsum()[-1]
        print("资金相对收益：%s VS %s" % (line_trend_key, line_bench_key))

        type_dict = {line_bench_key: stock_dat['benchmark_profit_log'].cumsum(),
                     line_trend_key: stock_dat['trend_profit_log'].cumsum()
                     }
        view_function = MplTypesDraw.mpl.route_output(u"line")
        view_function(stock_dat.index, type_dict, sub_graph)

    # 参照<9.1.5 度量策略的最大风险回撤>
    @app.route_types(u"close_retrace")  # relative_profit
    def close_retrace_graph(stock_dat, sub_graph, para_dat):
        # 度量策略最大风险回撤——收盘价最大回撤

        # 计算收盘价曲线当前的滚动最高值
        stock_dat['max_close'] = stock_dat['Close'].expanding().max()
        # 计算收盘价曲线在滚动最高值之后所回撤的百分比
        stock_dat['per_close'] = stock_dat['Close'] / stock_dat['max_close']

        # 计算并打印收盘价的最大回撤率
        min_point_df = stock_dat.sort_values(by=['per_close'])[0:1]
        min_point_close = min_point_df.per_close
        # min_point_close = stock_dat.sort_values(by=['per_close']).iloc[[0], stock_dat.columns.get_loc('per_close')]

        # 寻找出最大回撤率所对应的最高值交易日和最大回撤交易日，并打印显示
        max_point_df = stock_dat[stock_dat.index <= min_point_close.index[0]].sort_values(by=['Close'],
                                                                                          ascending=False)[0:1]
        max_point_close = max_point_df.Close
        # max_point_close = stock_dat[stock_dat.index <= min_point_close.index[0]].sort_values \
        #    (by=['Close'], ascending=False).iloc[[0], stock_dat.columns.get_loc('Close')]

        print("股价最大回撤%5.2f%% 从%s开始至%s结束" % ((1 - min_point_close.values) * 100, \
                                            max_point_close.index[0], min_point_close.index[0]))
        ##最大股价回撤 29.21% 从2018-06-12 00:00:00开始至2018-12-27 00:00:00结束

        type_dict = {'最大收盘价': stock_dat.max_close,
                     '收盘价': stock_dat.Close
                     }
        view_function = MplTypesDraw.mpl.route_output(u"line")
        view_function(stock_dat.index, type_dict, sub_graph)

        type_dict = {u"股价最大回撤\n{}".format(1 - min_point_close.values):
                               {'andata': min_point_df,
                                'va': 'top',
                                'xy_y': 'Close',
                                'xytext': (0,stock_dat['High'].mean()),
                                'fontsize': 8,
                                'arrow': dict(facecolor='green', shrink=0.1)
                                },
                    }
        view_function = MplTypesDraw.mpl.route_output(u"annotate")
        view_function(stock_dat.index, type_dict, sub_graph)

    @app.route_types(u"trade")
    def trade_graph(stock_dat, sub_graph, para_dat):
        # 交易获利/亏损区间可视化

        type_dict = {'signal': stock_dat.Signal,
                     'jdval': stock_dat.Close,
                     'va': 'top',
                     'xy_y': 'Close',
                     'xytext': (0,stock_dat['High'].mean()),
                     'fontsize': 8,
                     'arrow': dict(facecolor='yellow', shrink=0.1)
                     }
        view_function = MplTypesDraw.mpl.route_output(u"filltrade")
        view_function(stock_dat.index, type_dict, sub_graph)

    # 参照<9.1.2 交易概览信息的统计>
    def log_trade_info(self, stock_dat):

        signal_shift = stock_dat.Signal.shift(1)
        signal_shift.fillna(value=-1, inplace=True)  # 序列最前面的NaN值用-1填充
        list_signal = np.sign(stock_dat.Signal - signal_shift)

        buy_singal = stock_dat[list_signal.isin([1])]
        sell_singal = stock_dat[list_signal.isin([-1])]
        """
        trade_info = pd.DataFrame({'BuyTime': buy_singal.index.strftime("%y.%m.%d"),
                                   'SellTime': sell_singal.index.strftime("%y.%m.%d"),
                                   'BuyPrice': buy_singal.Close.values,
                                   'SellPrice': sell_singal.Close.values})
        """
        # 解决 ValueError: Length of values does not match length of index
        trade_info = pd.concat([pd.DataFrame({'BuyTime': buy_singal.index.strftime("%y.%m.%d")}),
                                pd.DataFrame({'SellTime': sell_singal.index.strftime("%y.%m.%d")}),
                                pd.DataFrame({'BuyPrice': buy_singal.Close.values}),
                                pd.DataFrame({'SellPrice': sell_singal.Close.values})], axis=1)

        trade_info['DiffPrice'] = trade_info.SellPrice - trade_info.BuyPrice
        trade_info['PctProfit'] = np.round(trade_info.DiffPrice / trade_info.BuyPrice*100, 2)

        win_count = (trade_info.DiffPrice >= 0).sum()
        loss_count = (trade_info.DiffPrice < 0).sum()
        win_profit = trade_info[trade_info.PctProfit >= 0].PctProfit.sum()
        loss_profit = trade_info[trade_info.PctProfit < 0].PctProfit.sum()

        for kl_index, info in trade_info.iterrows():
            print(f'策略信号-{kl_index}')
            print(f'买入时间：{info.BuyTime}, 买入价格：{info.BuyPrice}')
            print(f'卖出时间:{info.SellTime}，卖出价格：{info.SellPrice}')
            print(f'涨幅%：{info.PctProfit}')

        print(f'亏损次数:{loss_count}, 盈利次数:{win_count}, 胜率:{round(win_count / (win_count + loss_count)*100, 2)}%')
        print(f'平均亏损:{round((loss_profit / loss_count), 2)}% 平均盈利:{round((win_profit / win_count), 2)}%')

    def graph_attr(self, **kwargs):

        if 'title' in kwargs.keys():
            self.graph_curr.set_title(kwargs['title'])

        if 'legend' in kwargs.keys():
            self.graph_curr.legend(loc=kwargs['legend'], shadow=True)

        if 'xlabel' in kwargs.keys():
            self.graph_curr.set_xlabel(kwargs['xlabel'])

        self.graph_curr.set_ylabel(kwargs['ylabel'])
        self.graph_curr.set_xlim(0, len(self.df_ohlc.index))  # 设置一下x轴的范围
        self.graph_curr.set_xticks(range(0, len(self.df_ohlc.index), kwargs['xticks']))  # X轴刻度设定 每15天标一个日期

        if 'xticklabels' in kwargs.keys():
            self.graph_curr.set_xticklabels(
                [self.df_ohlc.index.strftime(kwargs['xticklabels'])[index] for index in
                 self.graph_curr.get_xticks()])  # 标签设置为日期

            # X-轴每个ticker标签都向右倾斜45度
            for label in self.graph_curr.xaxis.get_ticklabels():
                label.set_rotation(45)
                label.set_fontsize(10)  # 设置标签字体
        else:
            for label in self.graph_curr.xaxis.get_ticklabels():
                label.set_visible(False)
