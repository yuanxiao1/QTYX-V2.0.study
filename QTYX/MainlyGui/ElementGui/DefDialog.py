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

class MarketGraphDialog(wx.Dialog):  # 行情走势图参数配置

    def __init__(self, parent, title=u"自定义提示信息", size=(800, 100)):

        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 行情参数——日历控件时间周期
        self.dpc_end_time = wx.adv.DatePickerCtrl(self, -1,
                                                  style = wx.adv.DP_DROPDOWN|wx.adv.DP_SHOWCENTURY|wx.adv.DP_ALLOWNONE)#结束时间
        self.dpc_start_time = wx.adv.DatePickerCtrl(self, -1,
                                                    style = wx.adv.DP_DROPDOWN|wx.adv.DP_SHOWCENTURY|wx.adv.DP_ALLOWNONE)#起始时间

        self.start_date_box = wx.StaticBox(self, -1, u'开始日期(Start)')
        self.end_date_box = wx.StaticBox(self, -1, u'结束日期(End)')
        self.start_date_sizer = wx.StaticBoxSizer(self.start_date_box, wx.VERTICAL)
        self.end_date_sizer = wx.StaticBoxSizer(self.end_date_box, wx.VERTICAL)
        self.start_date_sizer.Add(self.dpc_start_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.end_date_sizer.Add(self.dpc_end_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        date_time_now = wx.DateTime.Now()  # wx.DateTime格式"03/03/18 00:00:00"
        self.dpc_end_time.SetValue(date_time_now)
        self.dpc_start_time.SetValue(date_time_now.SetYear(date_time_now.year - 1))

        # 行情参数——股票周期选择
        self.stock_period_box = wx.StaticBox(self, -1, u'股票周期')
        self.stock_period_sizer = wx.StaticBoxSizer(self.stock_period_box, wx.VERTICAL)
        self.stock_period_cbox = wx.ComboBox(self, -1, u"", choices=[u"30分钟", u"60分钟", u"日线", u"周线"])
        self.stock_period_cbox.SetSelection(2)
        self.stock_period_sizer.Add(self.stock_period_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 行情参数——股票复权选择
        self.stock_authority_box = wx.StaticBox(self, -1, u'股票复权')
        self.stock_authority_sizer = wx.StaticBoxSizer(self.stock_authority_box, wx.VERTICAL)
        self.stock_authority_cbox = wx.ComboBox(self, -1, u"", choices=[u"前复权", u"后复权", u"不复权"])
        self.stock_authority_cbox.SetSelection(2)
        self.stock_authority_sizer.Add(self.stock_authority_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.start_date_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.end_date_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stock_period_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stock_authority_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        self.SetSizer(self.FlexGridSizer)

    def feedback_paras(self):

        self.ochl_paras = dict()

        self.ochl_paras[u"股票周期"] = self.stock_period_cbox.GetStringSelection()
        self.ochl_paras[u"股票复权"] = self.stock_authority_cbox.GetStringSelection()
        self.ochl_paras[u"开始日期"] = self.dpc_start_time.GetValue()
        self.ochl_paras[u"结束日期"] = self.dpc_end_time.GetValue()

        return self.ochl_paras

class BacktGraphDialog(wx.Dialog):  # 行情走势图参数配置

    def __init__(self, parent, title=u"自定义提示信息", size=(600, 250)):

        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=3, cols=4, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 行情参数——日历控件时间周期
        self.dpc_end_time = wx.adv.DatePickerCtrl(self, -1,
                                                  style = wx.adv.DP_DROPDOWN|wx.adv.DP_SHOWCENTURY|wx.adv.DP_ALLOWNONE)#结束时间
        self.dpc_start_time = wx.adv.DatePickerCtrl(self, -1,
                                                    style = wx.adv.DP_DROPDOWN|wx.adv.DP_SHOWCENTURY|wx.adv.DP_ALLOWNONE)#起始时间

        self.start_date_box = wx.StaticBox(self, -1, u'开始日期(Start)')
        self.end_date_box = wx.StaticBox(self, -1, u'结束日期(End)')
        self.start_date_sizer = wx.StaticBoxSizer(self.start_date_box, wx.VERTICAL)
        self.end_date_sizer = wx.StaticBoxSizer(self.end_date_box, wx.VERTICAL)
        self.start_date_sizer.Add(self.dpc_start_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.end_date_sizer.Add(self.dpc_end_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        date_time_now = wx.DateTime.Now()  # wx.DateTime格式"03/03/18 00:00:00"
        self.dpc_end_time.SetValue(date_time_now)
        self.dpc_start_time.SetValue(date_time_now.SetYear(date_time_now.year - 1))

        # 行情参数——股票周期选择
        self.stock_period_box = wx.StaticBox(self, -1, u'股票周期')
        self.stock_period_sizer = wx.StaticBoxSizer(self.stock_period_box, wx.VERTICAL)
        self.stock_period_cbox = wx.ComboBox(self, -1, u"", choices=[u"30分钟", u"60分钟", u"日线", u"周线"])
        self.stock_period_cbox.SetSelection(2)
        self.stock_period_sizer.Add(self.stock_period_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 行情参数——股票复权选择
        self.stock_authority_box = wx.StaticBox(self, -1, u'股票复权')
        self.stock_authority_sizer = wx.StaticBoxSizer(self.stock_authority_box, wx.VERTICAL)
        self.stock_authority_cbox = wx.ComboBox(self, -1, u"", choices=[u"前复权", u"后复权", u"不复权"])
        self.stock_authority_cbox.SetSelection(2)
        self.stock_authority_sizer.Add(self.stock_authority_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        self.init_cash_box = wx.StaticBox(self, -1, u'初始资金')
        self.init_cash_sizer = wx.StaticBoxSizer(self.init_cash_box, wx.VERTICAL)
        self.init_cash_input = wx.TextCtrl(self, -1, "100000", style=wx.TE_LEFT)
        self.init_cash_sizer.Add(self.init_cash_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        self.init_stake_box = wx.StaticBox(self, -1, u'交易规模')
        self.init_stake_sizer = wx.StaticBoxSizer(self.init_stake_box, wx.VERTICAL)
        self.init_stake_input = wx.TextCtrl(self, -1, "all", style=wx.TE_LEFT)
        self.init_stake_sizer.Add(self.init_stake_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        self.init_slippage_box = wx.StaticBox(self, -1, u'滑点')
        self.init_slippage_sizer = wx.StaticBoxSizer(self.init_slippage_box, wx.VERTICAL)
        self.init_slippage_input = wx.TextCtrl(self, -1, "0.01", style=wx.TE_LEFT)
        self.init_slippage_sizer.Add(self.init_slippage_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        self.init_commission_box = wx.StaticBox(self, -1, u'手续费')
        self.init_commission_sizer = wx.StaticBoxSizer(self.init_commission_box, wx.VERTICAL)
        self.init_commission_input = wx.TextCtrl(self, -1, "0.0005", style=wx.TE_LEFT)
        self.init_commission_sizer.Add(self.init_commission_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        self.init_tax_box = wx.StaticBox(self, -1, u'印花税')
        self.init_tax_sizer = wx.StaticBoxSizer(self.init_tax_box, wx.VERTICAL)
        self.init_tax_input = wx.TextCtrl(self, -1, "0.001", style=wx.TE_LEFT)
        self.init_tax_sizer.Add(self.init_tax_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.start_date_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.end_date_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stock_period_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stock_authority_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)

        self.FlexGridSizer.Add(self.init_cash_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.init_stake_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.init_slippage_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.init_commission_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)

        self.FlexGridSizer.Add(self.init_tax_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)

        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)
        self.SetSizer(self.FlexGridSizer)

    def feedback_paras(self):

        self.ochl_paras = dict()

        self.ochl_paras[u"股票周期"] = self.stock_period_cbox.GetStringSelection()
        self.ochl_paras[u"股票复权"] = self.stock_authority_cbox.GetStringSelection()
        self.ochl_paras[u"开始日期"] = self.dpc_start_time.GetValue()
        self.ochl_paras[u"结束日期"] = self.dpc_end_time.GetValue()
        self.ochl_paras[u"初始资金"] = self.init_cash_input.GetValue()
        self.ochl_paras[u"交易规模"] = self.init_stake_input.GetValue()
        self.ochl_paras[u"滑点"] = self.init_slippage_input.GetValue()
        self.ochl_paras[u"手续费"] = self.init_commission_input.GetValue()
        self.ochl_paras[u"印花税"] = self.init_tax_input.GetValue()

        return self.ochl_paras