#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx
import os
import datetime
import numpy as np
import matplotlib.pyplot as plt


from CommIf.SysFile import Base_File_Oper
from MainlyGui.ElementGui.DefPanel import GroupPanel
# 分离控件事件中调用的子事件
from EventEngine.DefEvent import (
    EventHandle
)
from MultiGraphs.SignalOutput import CurHaveSig

def MessageDialog(info):
    # 提示对话框
    # info:提示内容
    back_info = ""
    dlg_mesg = wx.MessageDialog(None, info, u"温馨提示",
                                wx.YES_NO | wx.ICON_INFORMATION)
    if dlg_mesg.ShowModal() == wx.ID_YES:
        back_info = "点击Yes"
    else:
        back_info = "点击No"
    dlg_mesg.Destroy()
    return back_info

def ChoiceDialog(info, choice):

    dlg_mesg = wx.SingleChoiceDialog(None, info, u"单选提示", choice)
    dlg_mesg.SetSelection(0)  # default selection

    if dlg_mesg.ShowModal() == wx.ID_OK:
        select = dlg_mesg.GetStringSelection()
    else:
        select = None
    dlg_mesg.Destroy()
    return select

def ImportFileDiag():
    # 导入文件对话框
    # return:文件路径
    # wildcard = "CSV Files (*.xls)|*.xls"
    wildcard = "CSV Files (*.csv)|*.csv"
    dlg_mesg = wx.FileDialog(None, "请选择文件", os.getcwd(), "", wildcard,
                             wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST)  # 旧版 wx.OPEN wx.CHANGE_DIR
    if dlg_mesg.ShowModal() == wx.ID_OK:
        file_path = dlg_mesg.GetPath()
    else:
        file_path = ''
    dlg_mesg.Destroy()
    return file_path

class UserDialog(wx.Dialog):  # user-defined

    def __init__(self, parent, title=u"自定义提示信息", label=u"自定义日志", size=(700, 500)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        self.log_tx_input = wx.TextCtrl(self, -1, "", size=(600, 400), style=wx.TE_MULTILINE | wx.TE_READONLY)  # 多行|只读
        self.log_tx_input.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()

        self.dialog_info_box = wx.StaticBox(self, -1, label)
        self.dialog_info_sizer = wx.StaticBoxSizer(self.dialog_info_box, wx.VERTICAL)
        self.dialog_info_sizer.Add(self.log_tx_input, proportion=0, flag=wx.EXPAND|wx.ALL|wx.CENTER, border=10)
        self.dialog_info_sizer.Add(self.ok_btn, proportion=0, flag=wx.ALIGN_CENTER)
        self.SetSizer(self.dialog_info_sizer)

        self.disp_loginfo()

    def disp_loginfo(self):
        self.log_tx_input.Clear()
        self.log_tx_input.AppendText(Base_File_Oper.read_log_trade())


class ScanDialog(wx.Dialog):  # user-defined

    def __init__(self, parent, st_label, st_codes, st_period, st_auth, sdate_obj, edate_obj, title=u"自定义提示信息", label=u"自定义日志", size=(700, 500)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 初始化事件调用接口
        self.EventHandle = EventHandle()
        self.call_method = self.EventHandle.call_method
        self.event_task = self.EventHandle.event_task

        self.cur_have_sig = CurHaveSig()
        self.log_tx_input = wx.TextCtrl(self, -1, "", size=(600, 400), style=wx.TE_MULTILINE | wx.TE_READONLY)  # 多行|只读
        self.log_tx_input.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.ok_btn.Bind(wx.EVT_BUTTON, self.ev_stop)

        self.dialog_info_box = wx.StaticBox(self, -1, label)
        self.dialog_info_sizer = wx.StaticBoxSizer(self.dialog_info_box, wx.VERTICAL)
        self.dialog_info_sizer.Add(self.log_tx_input, proportion=0, flag=wx.EXPAND|wx.ALL|wx.CENTER, border=10)
        self.dialog_info_sizer.Add(self.ok_btn, proportion=0, flag=wx.ALIGN_CENTER)
        self.SetSizer(self.dialog_info_sizer)
        # 初始化变量
        self.st_codes = st_codes
        self.st_period = st_period
        self.st_auth = st_auth
        self.sdate_obj = sdate_obj
        self.edate_obj = edate_obj
        self.st_label = st_label
        # 开启定时器
        self.analy_timer = wx.Timer(self)  # 创建定时器
        self.Bind(wx.EVT_TIMER, self.ev_analy_timer, self.analy_timer)  # 绑定一个定时器事件
        self.gen_code = self.generate_codes
        self.analy_timer.Start(200)  # 启动定时器

    @property
    def generate_codes(self):
        for code in self.st_codes.values():
            yield code

    def ev_stop(self, event):
        self.analy_timer.Stop()  # 关闭定时器
        self.log_tx_input.AppendText("取消运行！\n")
        self.Destroy()

    def ev_analy_timer(self, event):

        try:
            code = next(self.gen_code)

            # 第二步:获取股票数据-调用sub event handle
            stock_dat = self.call_method(self.event_task['get_stock_dat'],
                                              st_code=code,
                                              st_period=self.st_period,
                                              st_auth=self.st_auth,
                                              sdate_obj=self.sdate_obj,
                                              edate_obj=self.edate_obj)

            view_function = self.cur_have_sig.ind.route_output(self.st_label)
            cont = view_function(stock_dat)
            self.log_tx_input.AppendText(code + " " + cont)

        except:
            self.analy_timer.Stop()  # 关闭定时器
            self.log_tx_input.AppendText("自选股票池扫描完成！\n")
            return

class ProgressDialog():

    def __init__(self, title=u"下载进度", maximum=1000):

        self.dialog = wx.ProgressDialog(title, "剩余时间", maximum,
                                        style=wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)

    def update_bar(self, count):
        self.dialog.Update(count)

    def close_bar(self):
        self.dialog.Destroy()

    def reset_range(self, maximum):
        self.dialog.SetRange(maximum)

class WebDialog(wx.Dialog):  # user-defined

    load_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + '/DataFiles/'

    def __init__(self, parent, title=u"Web显示", file_name='treemap_base.html', size=(1200, 900)):

        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        self.browser = wx.html2.WebView.New(self, -1, size=size)
        with open(self.load_path + file_name, 'r') as f:
            html_cont = f.read()
        self.browser.SetPage(html_cont, "")
        self.browser.Show()

class DouBottomDialog(wx.Dialog):  # 双底形态参数

    load_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + '/ConfigFiles/'

    def __init__(self, parent, title=u"自定义提示信息", size=(700, 750)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style = wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=10, cols=1, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 选取K线范围
        self.period_amount_box = wx.StaticBox(self, -1, "选取K线范围(日)")
        self.period_amount_sizer = wx.StaticBoxSizer(self.period_amount_box, wx.VERTICAL)
        self.period_amount_input = wx.TextCtrl(self, -1, "40", style=wx.TE_PROCESS_ENTER)
        self.period_amount_sizer.Add(self.period_amount_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 选取中间区域误差
        self.middle_err_box = wx.StaticBox(self, -1, "选取中间区域误差(日)")
        self.middle_err_sizer = wx.StaticBoxSizer(self.middle_err_box, wx.VERTICAL)
        self.middle_err_input = wx.TextCtrl(self, -1, "5", style=wx.TE_PROCESS_ENTER)
        self.middle_err_sizer.Add(self.middle_err_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 双底低点之间误差
        self.lowbetw_err_box = wx.StaticBox(self, -1, "双底低点之间误差%")
        self.lowbetw_err_sizer = wx.StaticBoxSizer(self.lowbetw_err_box, wx.VERTICAL)
        self.lowbetw_err_input = wx.TextCtrl(self, -1, "2", style=wx.TE_PROCESS_ENTER)
        self.lowbetw_err_sizer.Add(self.lowbetw_err_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 有效突破颈线幅度
        self.backcfm_thr_box = wx.StaticBox(self, -1, "有效突破颈线幅度%")
        self.backcfm_thr_sizer = wx.StaticBoxSizer(self.backcfm_thr_box, wx.VERTICAL)
        self.backcfm_thr_input = wx.TextCtrl(self, -1, "3", style=wx.TE_PROCESS_ENTER)
        self.backcfm_thr_sizer.Add(self.backcfm_thr_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 有效突破当天涨跌幅
        self.break_pctchg_box = wx.StaticBox(self, -1, "有效突破当天涨跌幅%")
        self.break_pctchg_sizer = wx.StaticBoxSizer(self.break_pctchg_box, wx.VERTICAL)
        self.break_pctchg_input = wx.TextCtrl(self, -1, "1", style=wx.TE_PROCESS_ENTER)
        self.break_pctchg_sizer.Add(self.break_pctchg_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 有效突破成交量阈值
        self.volume_thr_box = wx.StaticBox(self, -1, "有效突破成交量阈值(大于平均%)")
        self.volume_thr_sizer = wx.StaticBoxSizer(self.volume_thr_box, wx.VERTICAL)
        self.volume_thr_input = wx.TextCtrl(self, -1, "5", style=wx.TE_PROCESS_ENTER)
        self.volume_thr_sizer.Add(self.volume_thr_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 设置使能回测所需交易日
        self.backtest_days_box = wx.StaticBox(self, -1, "设置使能回测所需交易日数量")
        self.backtest_days_sizer = wx.StaticBoxSizer(self.backtest_days_box, wx.VERTICAL)
        self.backtest_days_input = wx.TextCtrl(self, -1, "40", style=wx.TE_PROCESS_ENTER)
        self.backtest_days_sizer.Add(self.backtest_days_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        self.save_cond_box = wx.RadioBox(self, -1, label=u'选股结果保存', choices=["出现双底即保存","满足突破幅度才保存",
                                                                              "满足首次突破才保存", "满足突破涨幅才保存",
                                                                              "满足突破放量才保存"],
                                                                     majorDimension = 5, style = wx.RA_SPECIFY_ROWS)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.period_amount_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.middle_err_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.lowbetw_err_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.backcfm_thr_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.break_pctchg_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.volume_thr_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.backtest_days_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.save_cond_box, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        # 声明图片对象
        image = wx.Image(self.load_path+r'双底形态识别模型图.png', wx.BITMAP_TYPE_PNG)
        #print('图片的尺寸为{0}x{1}'.format(image.GetWidth(),image.GetHeight()))

        image.Rescale(image.GetWidth(),image.GetHeight())
        embed_pic = image.ConvertToBitmap()
        # 显示图片
        self.embed_bitmap = wx.StaticBitmap(self,-1, bitmap=embed_pic, size=(image.GetWidth(), image.GetHeight()))

        # 添加参数布局
        self.vbox_sizer = wx.BoxSizer(wx.HORIZONTAL)  # 纵向box
        self.vbox_sizer.Add(self.FlexGridSizer, proportion=1, flag=wx.EXPAND | wx.BOTTOM, border=2)
        self.vbox_sizer.Add(self.embed_bitmap, proportion=1, flag=wx.EXPAND | wx.BOTTOM, border=2)

        self.SetSizer(self.vbox_sizer)

    def feedback_paras(self):

        self.bottom_para = dict()

        self.bottom_para[u"选取K线范围"] = int(self.period_amount_input.GetValue())
        self.bottom_para[u"选取中间区域误差"] = int(self.middle_err_input.GetValue())
        self.bottom_para[u"双底低点之间误差"] = float(self.lowbetw_err_input.GetValue())
        self.bottom_para[u"有效突破当天涨跌幅"] = float(self.break_pctchg_input.GetValue())
        self.bottom_para[u"有效突破颈线幅度"] = int(self.backcfm_thr_input.GetValue())
        self.bottom_para[u"有效突破成交量阈值"] = float(self.volume_thr_input.GetValue())
        self.bottom_para[u"双底回测使能所需交易日"] = int(self.backtest_days_input.GetValue())
        self.bottom_para[u"选股结果保存"] = self.save_cond_box.GetStringSelection()

        return self.bottom_para

class RpsTop10Dialog(wx.Dialog):  # RPS-10参数

    def __init__(self, parent, title=u"自定义提示信息", size=(250, 360)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=6, cols=1, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 过滤次新股
        self.filter_list_time = wx.adv.DatePickerCtrl(self, -1,
                                                  style = wx.adv.DP_DROPDOWN|wx.adv.DP_SHOWCENTURY|wx.adv.DP_ALLOWNONE)#结束时间

        self.filter_list_box = wx.StaticBox(self, -1, u'上市时间\n(过滤该时间之后上市的股票)')
        self.filter_list_sizer = wx.StaticBoxSizer(self.filter_list_box, wx.VERTICAL)
        self.filter_list_sizer.Add(self.filter_list_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        date_time_now = wx.DateTime.Now()  # wx.DateTime格式"03/03/18 00:00:00"
        self.filter_list_time.SetValue(date_time_now.SetYear(date_time_now.year - 1))

        # 选取涨跌幅滚动周期
        self.period_roll_box = wx.StaticBox(self, -1, "选取涨跌幅滚动周期")
        self.period_roll_sizer = wx.StaticBoxSizer(self.period_roll_box, wx.VERTICAL)
        self.period_roll_input = wx.TextCtrl(self, -1, "20", style=wx.TE_PROCESS_ENTER)
        self.period_roll_sizer.Add(self.period_roll_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 选取显示的排名范围
        self.sel_order_box = wx.StaticBox(self, -1, "选择观测的排名范围")
        self.sel_order_sizer = wx.StaticBoxSizer(self.sel_order_box, wx.VERTICAL)
        self.sel_order_val = [u"前10", u"前20", u"前30", u"前40", u"前50"]
        self.sel_order_cmbo = wx.ComboBox(self, -1, u"前10", choices=self.sel_order_val,
                                            style=wx.CB_SIMPLE | wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择操作系统
        self.sel_order_sizer.Add(self.sel_order_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 输入跟踪排名的代码
        self.track_code_box = wx.StaticBox(self, -1, u'跟踪股票代码')
        self.track_code_sizer = wx.StaticBoxSizer(self.track_code_box, wx.VERTICAL)
        self.track_code_input = wx.TextCtrl(self, -1, "000400.SZ", style=wx.TE_PROCESS_ENTER)
        self.track_code_sizer.Add(self.track_code_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.filter_list_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.period_roll_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.sel_order_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.track_code_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        self.SetSizer(self.FlexGridSizer)

    def feedback_paras(self):

        self.rps_para = dict()

        filter_obj = self.filter_list_time.GetValue()
        filter_val = datetime.datetime(filter_obj.year, filter_obj.month + 1, filter_obj.day)

        self.rps_para[u"过滤次新股上市时间"] = int(filter_val.strftime('%Y%m%d'))
        self.rps_para[u"选取涨跌幅滚动周期"] = int(self.period_roll_input.GetValue())
        self.rps_para[u"选取显示的排名范围"] = (int(self.sel_order_cmbo.GetSelection())+1)*10
        self.rps_para[u"输入跟踪排名的代码"] = self.track_code_input.GetValue()

        return self.rps_para

class TradeConfDialog(wx.Dialog):  # 交易参数

    def __init__(self, parent, code="", name="", direct="买", price="", amount="100",
                                    title=u"自定义提示信息", size=(250, 500)):

        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=9, cols=1, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 股票代码
        self.stock_code_box = wx.StaticBox(self, -1, "股票代码")
        self.stcok_code_sizer = wx.StaticBoxSizer(self.stock_code_box, wx.VERTICAL)
        self.stcok_code_input = wx.TextCtrl(self, -1, code, style=wx.TE_READONLY)
        self.stcok_code_sizer.Add(self.stcok_code_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 股票名称
        self.stock_name_box = wx.StaticBox(self, -1, "股票名称")
        self.stcok_name_sizer = wx.StaticBoxSizer(self.stock_name_box, wx.VERTICAL)
        self.stcok_name_input = wx.TextCtrl(self, -1, name, style=wx.TE_READONLY)
        self.stcok_name_sizer.Add(self.stcok_name_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 买或卖
        self.bs_direct_box = wx.StaticBox(self, -1, "买/卖")
        self.bs_direct_sizer = wx.StaticBoxSizer(self.bs_direct_box, wx.VERTICAL)
        self.bs_direct_val = [u"买", u"卖"]
        self.bs_direct_cmbo = wx.ComboBox(self, -1, direct, choices=self.bs_direct_val,
                                            style=wx.CB_SIMPLE | wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择操作系统
        self.bs_direct_sizer.Add(self.bs_direct_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 价格
        self.trade_price_box = wx.StaticBox(self, -1, "价格")
        self.trade_price_sizer = wx.StaticBoxSizer(self.trade_price_box, wx.VERTICAL)
        self.trade_price_input = wx.TextCtrl(self, -1, str(price), style=wx.TE_PROCESS_ENTER)
        self.trade_price_sizer.Add(self.trade_price_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 数量
        self.trade_amount_box = wx.StaticBox(self, -1, "数量(股)")
        self.trade_amount_sizer = wx.StaticBoxSizer(self.trade_amount_box, wx.VERTICAL)
        self.trade_amount_input = wx.TextCtrl(self, -1, str(amount), style=wx.TE_PROCESS_ENTER)
        self.trade_amount_sizer.Add(self.trade_amount_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 策略跟踪
        self.trace_strategy_box = wx.StaticBox(self, -1, u'自定义策略跟踪')
        self.trace_strategy_sizer = wx.StaticBoxSizer(self.trace_strategy_box, wx.VERTICAL)
        self.trace_strategy_val = [u"自定义策略1", u"自定义策略2", u"自定义策略3"]
        self.trace_strategy_cmbo = wx.ComboBox(self, -1, u"自定义策略1", choices=self.trace_strategy_val,
                                          style=wx.CB_SIMPLE | wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择操作系统
        self.trace_strategy_sizer.Add(self.trace_strategy_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 自动交易
        self.auto_trade_box = wx.StaticBox(self, -1, u'是否自动交易')
        self.auto_trade_sizer = wx.StaticBoxSizer(self.auto_trade_box, wx.HORIZONTAL)
        self.auto_trade_chk = wx.CheckBox(self, label='确定执行')
        self.auto_trade_chk.Bind(wx.EVT_CHECKBOX, self._ev_auto_trade)  # 绑定复选框事件
        self.auto_trade_sizer.Add(self.auto_trade_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.stcok_code_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stcok_name_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.bs_direct_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.trade_price_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.trade_amount_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.trace_strategy_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.auto_trade_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        self.SetSizer(self.FlexGridSizer)

    def _ev_auto_trade(self, event):

        MessageDialog("执行自动交易请参考公众号文章部署环境！")

    def execute_paras(self):

        name = self.stcok_name_input.GetValue()
        self.trade_para = {name:{}}

        self.trade_para[name][u"code"] = self.stcok_code_input.GetValue()
        self.trade_para[name][u"direct"] = self.bs_direct_cmbo.GetStringSelection()
        self.trade_para[name][u"price"] = float(self.trade_price_input.GetValue())
        self.trade_para[name][u"amount"] = int(self.trade_amount_input.GetValue())
        self.trade_para[name][u"trace_strategy"] = self.trace_strategy_cmbo.GetStringSelection()
        self.trade_para[name][u"auto_trade"] = self.auto_trade_chk.GetValue()

        return self.trade_para

class HoldConfDialog(wx.Dialog):  # 持有参数

    def __init__(self, parent, code="", name="", exceed=u"", retreat="", price="", highest="",
                                    title=u"自定义提示信息", size=(250, 700)):

        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=12, cols=1, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 股票代码
        self.stock_code_box = wx.StaticBox(self, -1, "股票代码")
        self.stcok_code_sizer = wx.StaticBoxSizer(self.stock_code_box, wx.VERTICAL)
        self.stcok_code_input = wx.TextCtrl(self, -1, code, style=wx.TE_READONLY)
        self.stcok_code_sizer.Add(self.stcok_code_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 股票名称
        self.stock_name_box = wx.StaticBox(self, -1, "股票名称")
        self.stcok_name_sizer = wx.StaticBoxSizer(self.stock_name_box, wx.VERTICAL)
        self.stcok_name_input = wx.TextCtrl(self, -1, name, style=wx.TE_READONLY)
        self.stcok_name_sizer.Add(self.stcok_name_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 止盈方式
        self.stop_profit_box = wx.StaticBox(self, -1, "止盈模式")
        self.stop_profit_sizer = wx.StaticBoxSizer(self.stop_profit_box, wx.VERTICAL)
        self.stop_profit_val = [u"固定比例"]
        self.stop_profit_cmbo = wx.ComboBox(self, -1, self.stop_profit_val[0], choices=self.stop_profit_val,
                                            style=wx.CB_SIMPLE | wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择操作系统
        self.stop_profit_sizer.Add(self.stop_profit_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 止损方式
        self.stop_loss_box = wx.StaticBox(self, -1, "止损模式")
        self.stop_loss_sizer = wx.StaticBoxSizer(self.stop_loss_box, wx.VERTICAL)
        self.stop_loss_val = [u"回撤比例"]
        self.stop_loss_cmbo = wx.ComboBox(self, -1, self.stop_loss_val[0], choices=self.stop_loss_val,
                                            style=wx.CB_SIMPLE | wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择操作系统
        self.stop_loss_sizer.Add(self.stop_loss_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 盈利百分比
        self.exceed_per_box = wx.StaticBox(self, -1, "盈利幅度%")
        self.exceed_per_sizer = wx.StaticBoxSizer(self.exceed_per_box, wx.VERTICAL)
        self.exceed_per_input = wx.TextCtrl(self, -1, str(exceed), style=wx.TE_PROCESS_ENTER)
        self.exceed_per_sizer.Add(self.exceed_per_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 回撤百分比
        self.retreat_per_box = wx.StaticBox(self, -1, "回撤幅度%")
        self.retreat_per_sizer = wx.StaticBoxSizer(self.retreat_per_box, wx.VERTICAL)
        self.retreat_per_input = wx.TextCtrl(self, -1, str(retreat), style=wx.TE_PROCESS_ENTER)
        self.retreat_per_sizer.Add(self.retreat_per_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 买入价格
        self.buy_price_box = wx.StaticBox(self, -1, "买入价格")
        self.buy_price_sizer = wx.StaticBoxSizer(self.buy_price_box, wx.VERTICAL)
        self.buy_price_input = wx.TextCtrl(self, -1, str(price), style=wx.TE_READONLY)
        self.buy_price_sizer.Add(self.buy_price_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 持有后最高价
        self.highest_price_box = wx.StaticBox(self, -1, "持有后最高价")
        self.highest_price_sizer = wx.StaticBoxSizer(self.highest_price_box, wx.VERTICAL)
        self.highest_price_input = wx.TextCtrl(self, -1, str(highest), style=wx.TE_READONLY)
        self.highest_price_sizer.Add(self.highest_price_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 策略跟踪
        self.trace_strategy_box = wx.StaticBox(self, -1, u'自定义策略跟踪')
        self.trace_strategy_sizer = wx.StaticBoxSizer(self.trace_strategy_box, wx.VERTICAL)
        self.trace_strategy_val = [u"自定义策略1", u"自定义策略2", u"自定义策略3"]
        self.trace_strategy_cmbo = wx.ComboBox(self, -1, u"自定义策略1", choices=self.trace_strategy_val,
                                          style=wx.CB_SIMPLE | wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择操作系统
        self.trace_strategy_sizer.Add(self.trace_strategy_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 自动交易
        self.auto_trade_box = wx.StaticBox(self, -1, u'是否自动交易')
        self.auto_trade_sizer = wx.StaticBoxSizer(self.auto_trade_box, wx.HORIZONTAL)
        self.auto_trade_chk = wx.CheckBox(self, label='确定执行')
        self.auto_trade_chk.Bind(wx.EVT_CHECKBOX, self._ev_auto_trade)  # 绑定复选框事件
        self.auto_trade_sizer.Add(self.auto_trade_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.stcok_code_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stcok_name_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stop_profit_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stop_loss_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.exceed_per_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.retreat_per_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.buy_price_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.highest_price_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.trace_strategy_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.auto_trade_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        self.SetSizer(self.FlexGridSizer)

    def _ev_auto_trade(self, event):

        MessageDialog("执行自动交易请参考公众号文章部署环境！")

    def execute_paras(self):

        name = self.stcok_name_input.GetValue()
        self.hold_para = {name:{}}

        self.hold_para[name][u"code"] = self.stcok_code_input.GetValue()
        self.hold_para[name][u"exceed"] = int(self.exceed_per_input.GetValue())
        self.hold_para[name][u"retreat"] = int(self.retreat_per_input.GetValue())
        self.hold_para[name][u"price"] = float(self.highest_price_input.GetValue())
        self.hold_para[name][u"trace_strategy"] = self.trace_strategy_cmbo.GetStringSelection()
        self.hold_para[name][u"auto_trade"] = self.auto_trade_chk.GetValue()

        return self.hold_para

class ViewGripDiag(wx.Dialog):

    def __init__(self, parent, title=u"表格数据显示", update_df=[], size=(750, 500)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style = wx.DEFAULT_FRAME_STYLE)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.data_to_grid(update_df)

        sizer.Add(self.grid, flag=wx.ALIGN_CENTER)

        self.SetSizer(sizer)

    def data_to_grid(self, df):

        self.grid = wx.grid.Grid(self, -1)

        if df.empty != True:
            self.list_columns = df.columns.tolist()
            self.grid.CreateGrid(df.shape[0], df.shape[1]) # 初始化时默认生成

            for col, series in df.iteritems():  # 将DataFrame迭代为(列名, Series)对
                m = self.list_columns.index(col)
                self.grid.SetColLabelValue(m, col)
                for n, val in enumerate(series):
                    self.grid.SetCellValue(n, m, str(val))
                self.grid.AutoSizeColumn(m, True)  # 自动调整列尺寸

