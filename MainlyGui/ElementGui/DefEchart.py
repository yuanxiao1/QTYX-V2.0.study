#! /usr/bin/env python 
#-*- encoding: utf-8 -*- 
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx
import os
import wx.adv
import wx.grid
import wx.html2
# Overlap+Grid方法绘制交易行情界面
from pyecharts.charts import Grid, Line, Bar, EffectScatter, Kline  # newest 1.7.0
from pyecharts import options as opts
from pyecharts.charts import TreeMap

from CommIf.SysFile import Base_File_Oper

load_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + '/DataFiles/'

class WebPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=-1)

        self.panel = wx.Panel(parent, -1)
        self.browser = None # 初始化浏览器对象

    def bind_browser(self, obj): # 绑定浏览器对象
        self.browser = obj

    def clear_subgraph(self):
        # 无需操作
        pass

    def update_subgraph(self):
        pass

    def draw_subgraph(self, stockdat, st_name, st_kylabel):
        # 绘制web多子图页面

        stockdat['Ma20'] = stockdat.Close.rolling(window=20).mean()
        stockdat['Ma30'] = stockdat.Close.rolling(window=30).mean()
        stockdat['Ma60'] = stockdat.Close.rolling(window=60).mean()

        volume_rise = [stockdat.Volume[x] if stockdat.Close[x] > stockdat.Open[x] else "0" for x in
                       range(0, len(stockdat.index))]
        volume_drop = [stockdat.Volume[x] if stockdat.Close[x] <= stockdat.Open[x] else "0" for x in
                       range(0, len(stockdat.index))]

        ohlc = list(zip(stockdat.Open, stockdat.Close, stockdat.Low, stockdat.High))
        dates = stockdat.index.strftime('%Y-%m-%d %H:%M')

        kline = (
            Kline()
                .add_xaxis(dates.tolist())
                .add_yaxis(
                "kline",
                ohlc,
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(type_="max", value_dim="close")]  # 标注最大值线
                ),
            )
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                    xaxis_opts=opts.AxisOpts(is_scale=True, is_show=False),
                    yaxis_opts=opts.AxisOpts(is_scale=True,
                                         splitarea_opts=opts.SplitAreaOpts(
                                             is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                                            )
                                         ),
                legend_opts=opts.LegendOpts(orient="vertical", pos_top="20%", pos_right="0%"),  # 调整图例的位置
                title_opts=opts.TitleOpts(title=st_name + "" + st_kylabel + "" + "行情显示图"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line")
            )
        )
        line = (
            Line()
                .add_xaxis(dates.tolist())
                .add_yaxis("Ma20", stockdat["Ma20"].tolist())
                .add_yaxis("Ma30", stockdat["Ma30"].tolist())
                .add_yaxis("Ma60", stockdat["Ma60"].tolist())
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        )
        bar = (
            Bar()
                .add_xaxis(dates.tolist())
                .add_yaxis("rvolume", volume_rise, stack="stack1", category_gap="50%")  # 堆积柱形图
                .add_yaxis("dvolume", volume_drop, stack="stack1", category_gap="50%")  # 堆积柱形图
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                # xaxis_index=[0, 1] 同时显示两幅图
                .set_global_opts(datazoom_opts=[opts.DataZoomOpts(xaxis_index=[0, 1], is_show=True)],  # 图表数据缩放
                                 legend_opts=opts.LegendOpts(orient="vertical", pos_right="0%")

                                 )
        )

        overlap_1 = kline.overlap(line)
        grid = (
            Grid(init_opts=opts.InitOpts(height="450px", width = "800px")) # 调整尺寸-height和width数值
                .add(bar, grid_opts=opts.GridOpts(pos_top="60%"), grid_index=0)
                .add(overlap_1, grid_opts=opts.GridOpts(pos_bottom="40%"), grid_index=1)
                .render(load_path + r"grid_vertical.html")  # raw string 非转义 string
        )

        with open(load_path + "grid_vertical.html", 'r') as f:
            html_cont = f.read()
        self.browser.SetPage(html_cont, "")
        self.browser.Show()

class WebGraphs(wx.Panel):

    def __init__(self, parent):

        # 创建FlexGridSizer布局网格 vgap定义垂直方向上行间距/hgap定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=2, cols=2, vgap=1, hgap=1)

        self.DispPanel0 = WebPanel(parent)  # 自定义
        self.DispPanel1 = WebPanel(parent)  # 自定义
        self.DispPanel2 = WebPanel(parent)  # 自定义
        self.DispPanel3 = WebPanel(parent)  # 自定义

        sys_para = Base_File_Oper.load_sys_para("sys_para.json")

        # 调整尺寸-size(x,y)数值 体现每个panel的大小
        self.DispPanel0.bind_browser(wx.html2.WebView.New(self.DispPanel0, -1, size=(sys_para["multi-panels"]["web_size_x"],
                                                                                     sys_para["multi-panels"]["web_size_y"])))
        self.DispPanel1.bind_browser(wx.html2.WebView.New(self.DispPanel1, -1, size=(sys_para["multi-panels"]["web_size_x"],
                                                                                     sys_para["multi-panels"]["web_size_y"])))
        self.DispPanel2.bind_browser(wx.html2.WebView.New(self.DispPanel2, -1, size=(sys_para["multi-panels"]["web_size_x"],
                                                                                     sys_para["multi-panels"]["web_size_y"])))
        self.DispPanel3.bind_browser(wx.html2.WebView.New(self.DispPanel3, -1, size=(sys_para["multi-panels"]["web_size_x"],
                                                                                     sys_para["multi-panels"]["web_size_y"])))

        # 加入Sizer中
        self.FlexGridSizer.Add(self.DispPanel0, proportion=1, border=2,
                               flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.FlexGridSizer.Add(self.DispPanel1, proportion=1, border=2,
                               flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.FlexGridSizer.Add(self.DispPanel2, proportion=1, border=2,
                               flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.FlexGridSizer.Add(self.DispPanel3, proportion=1, border=2,
                               flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)


class Pyechart_Drive():

    @staticmethod
    def TreeMap_Handle(multi_data=[], title="所属行业-个股-涨幅%", ser_name="行业板块"):

        c = (
            TreeMap(init_opts=opts.InitOpts(width="1280px", height="720px"))
                .add(series_name=ser_name,
                     data=multi_data,
                     visual_min=300,
                     leaf_depth=1,
                     # 标签居中为 position = "inside"
                     label_opts=opts.LabelOpts(position="inside")
                     )
                .set_global_opts(
                legend_opts=opts.LegendOpts(is_show=False),
                title_opts=opts.TitleOpts(title=title)
            )
                .render(load_path + "treemap_base.html")
        )

