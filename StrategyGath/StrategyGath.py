#! /usr/bin/env python 
#-*- encoding: utf-8 -*- 
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import talib

class Base_Strategy_Group():

    # 参照<9.2.2 唐奇安通道突破策略的实现>
    @staticmethod
    def get_ndays_signal(stock_dat, N1=15, N2=5):
        # 海龟策略-唐奇安通道突破(N日突破) 买入/卖出信号
        stock_dat['N1_High'] = stock_dat.High.rolling(window=N1).max()  # 计算最近N1个交易日最高价
        expan_max = stock_dat.High.expanding().max()  # 滚动计算当前交易日为止的最大值
        stock_dat['N1_High'].fillna(value=expan_max, inplace=True)  # 填充前N1个nan
        #print(stock_dat.head())
        """
                    High   Low  Open  Close   Volume  N1_High
        Date                                                 
        2018-06-01  47.3  46.3  47.3   46.6  5.0e+05     47.3
        2018-06-04  48.3  47.0  47.0   47.8  1.0e+06     48.3
        2018-06-05  48.8  47.9  48.0   48.5  1.0e+06     48.8
        2018-06-06  48.8  48.1  48.5   48.4  5.5e+05     48.8
        2018-06-07  48.9  47.9  48.8   48.0  5.6e+05     48.9
        """

        stock_dat['N2_Low'] = stock_dat.Low.rolling(window=N2).min()  # 计算最近N2个交易日最低价
        expan_min = stock_dat.Low.expanding().min()
        stock_dat['N2_Low'].fillna(value=expan_min, inplace=True)  # 目前出现过的最小值填充前N2个nan
        # print(stock_dat.head())
        """
                    High   Low  Open   ...     Volume  N1_High  N2_Low
        Date                           ...                            
        2018-06-01  47.3  46.3  47.3   ...    5.0e+05     47.3    46.3
        2018-06-04  48.3  47.0  47.0   ...    1.0e+06     48.3    46.3
        2018-06-05  48.8  47.9  48.0   ...    1.0e+06     48.8    46.3
        2018-06-06  48.8  48.1  48.5   ...    5.5e+05     48.8    46.3
        2018-06-07  48.9  47.9  48.8   ...    5.6e+05     48.9    46.3
    
        [5 rows x 7 columns]
        """
        # 收盘价超过N1最高价 买入股票
        buy_index = stock_dat[stock_dat.Close > stock_dat.N1_High.shift(1)].index
        # 收盘价超过N2最低价 卖出股票
        sell_index = stock_dat[stock_dat.Close < stock_dat.N2_Low.shift(1)].index

        # print(f'Buy-Time: \n {buy_index}')
        # print(f'Sell-Time: \n {sell_index}')

        stock_dat.loc[buy_index, 'Signal'] = 1
        stock_dat.loc[sell_index, 'Signal'] = -1

        stock_dat['Signal'] = stock_dat.Signal.shift(1)
        print(stock_dat.head(10))
        # print(stock_dat[stock_dat['signal'].notna()])
        stock_dat['Signal'].fillna(method='ffill', inplace=True)  # 与前面元素值保持一致
        stock_dat['Signal'].fillna(value=-1, inplace=True)  # 序列最前面几个NaN值用-1填充

        print(stock_dat.head(10))

        return stock_dat

    # 参照<9.3.2 ATR止盈/止损策略的实现>
    @staticmethod
    def get_ndays_atr_signal(stock_dat, N1=15, N2=5, n_win=3.4, n_loss=1.8):
        # 海龟策略-唐奇安通道突破(N日突破) 买入/卖出信号
        stock_dat['N1_High'] = stock_dat.High.rolling(window=N1).max()  # 计算最近N1个交易日最高价
        expan_max = stock_dat.High.expanding().max()  # 滚动计算当前交易日为止的最大值
        stock_dat['N1_High'].fillna(value=expan_max, inplace=True)  # 填充前N1个nan
        stock_dat['N2_Low'] = stock_dat.Low.rolling(window=N2).min()  # 计算最近N2个交易日最低价
        expan_min = stock_dat.Low.expanding().min()
        stock_dat['N2_Low'].fillna(value=expan_min, inplace=True)  # 目前出现过的最小值填充前N2个nan

        stock_dat['ATR21'] = talib.ATR(stock_dat.High.values, stock_dat.Low.values, stock_dat.Close.values,
                                        timeperiod=21)  # 计算ATR21
        # 收盘价超过N1最高价 买入股票
        buy_index = stock_dat[stock_dat.Close > stock_dat.N1_High.shift(1)].index
        # 收盘价超过N2最低价 卖出股票
        sell_index = stock_dat[stock_dat.Close < stock_dat.N2_Low.shift(1)].index
        #print(f'Buy-Time: \n {buy_index}')
        #print(f'Sell-Time: \n {sell_index}')

        stock_dat.loc[buy_index, 'Signal'] = 1
        stock_dat.loc[sell_index, 'Signal'] = -1
        stock_dat['Signal'] = stock_dat.Signal.shift(1)

        #print(stock_dat[stock_dat['signal'].notna()])
        buy_price = 0

        for kl_index, today in stock_dat.iterrows():
            #if today.Close > today.N1_High:
            if (buy_price == 0) and (today.Signal == 1):
                buy_price = today.Close
                #stockdata.loc[kl_index, 'signal'] = 1
            # 到达收盘价少于买入价后触发卖出
            elif (buy_price != 0) and (buy_price > today.Close) and ((buy_price - today.Close) > n_loss * today.ATR21):
                print(f'止损时间:{kl_index.strftime("%y.%m.%d")} 止损价格:{round(today.Close, 2)}')
                stock_dat.loc[kl_index, 'Signal'] = -1
                buy_price = 0
            # 到达收盘价多于买入价后触发卖出
            elif (buy_price != 0) and (buy_price < today.Close) and ((today.Close - buy_price) > n_win * today.ATR21):
                print(f'止盈时间:{kl_index.strftime("%y.%m.%d")} 止盈价格:{round(today.Close, 2)}')
                stock_dat.loc[kl_index, 'Signal'] = -1
                buy_price = 0
            elif (buy_price != 0) and (today.Signal == -1):
                stock_dat.loc[kl_index, 'Signal'] = -1
                buy_price = 0
            else:
                pass

        stock_dat['Signal'].fillna(method='ffill', inplace=True)  # 与前面元素值保持一致
        stock_dat['Signal'].fillna(value=-1, inplace=True)  # 序列最前面几个NaN值用0填充

        return stock_dat