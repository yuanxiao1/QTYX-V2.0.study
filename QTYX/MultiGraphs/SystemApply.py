#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import sys, os
from MultiGraphs.MarketGraph import MarketGraphIf
from MultiGraphs.BacktsGraph import BacktsGraphIf


class Sys_MultiGraph(MarketGraphIf, BacktsGraphIf):

    rel_path = os.path.dirname(os.path.dirname(__file__)) + '/ConfigFiles/'

    # 通读<8.1 定制可视化接口> -- 代码具体出现于<9.1.6 回测界面的自定义设计>
    def back_graph_run(self, stock_data, **kwargs):
        # 绘制子图
        self.df_ohlc = stock_data

        # 临时把标准输出重定向到一个文件，然后再恢复正常
        with open(Sys_MultiGraph.rel_path + 'logtrade.txt', 'w', encoding='gbk') as f:
            oldstdout = sys.stdout
            sys.stdout = f
            try:
                #self.log_trade_info(self.df_ohlc)
                for key in kwargs:
                    self.graph_curr = self.graph_dict[kwargs[key]['graph_name']]
                    self.graph_curr.clear() # 先清除原图像
                    for path, val in kwargs[key]['graph_type'].items():
                        view_function = BacktsGraphIf.app.route_output(path)
                        view_function(self.df_ohlc, self.graph_curr, val)
                    self.graph_attr(**kwargs[key])
                #plt.show()
            finally:
                sys.stdout = oldstdout

        """
        print("kwargs %s-->%s" % (key, kwargs[key]))
        #globals().get('self.%s' % key)(**kwargs[key])
        eval('self.%s' % key)()
        #self.kline_draw(**kwargs[key])
        """

    # 参考第8章
    def firm_graph_run(self, stock_data, **kwargs):
        # 绘制子图
        self.df_ohlc = stock_data
        for key in kwargs:
            self.graph_curr = self.graph_dict[kwargs[key]['graph_name']]
            self.graph_curr.clear()  # 先清除原图像
            for path, val in kwargs[key]['graph_type'].items():
                view_function = MarketGraphIf.app.route_output(path)
                view_function(self.df_ohlc, self.graph_curr, val)
            self.graph_attr(**kwargs[key])
        #plt.show()