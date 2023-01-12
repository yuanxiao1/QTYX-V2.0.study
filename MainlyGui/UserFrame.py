#! /usr/bin/env python 
#-*- encoding: utf-8 -*- 
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx
import wx.adv
import wx.grid
import wx.html2
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import webbrowser
from importlib import reload
from datetime import datetime
import threading
import queue

from ApiData.Tushare import basic_code_list

from MainlyGui.ElementGui.DefPanel import (
    SubGraphs,
    Sys_Panel
)

from MainlyGui.ElementGui.DefEchart import (
    WebGraphs
)

from MainlyGui.ElementGui.DefTreelist import (
    CollegeTreeListCtrl, CollegeTreeListCtrl2
)

from MainlyGui.ElementGui.DefGrid import (
    GridTable
)

from MainlyGui.ElementGui.DefEchart import (
    Pyechart_Drive
)

from MainlyGui.ElementGui.DefDialog import (
    ScanDialog,
    UserDialog, MessageDialog, ImportFileDiag, ProgressDialog, ChoiceDialog,
    WebDialog, DouBottomDialog, RpsTop10Dialog, ViewGripDiag,
)

from MainlyGui.ElementGui.DefParaDialog import (MarketGraphDialog, BacktGraphDialog, PattenSelDialog)

from MainlyGui.ElementGui.DefProgress import ProgressBarDialog, ProgressBarThread

from MainlyGui.ElementGui.DefListBox import ClassifySelectDiag

from ApiData.Tushare import (
    Tspro_Backend,
    Tsorg_Backend
)

from ApiData.CrawerDaily import CrawerDailyBackend

from ApiData.Csvdata import (
    Csv_Backend
)

# 分离控件事件中调用的子事件
from EventEngine.DefEvent import (
    EventHandle
)
from StrategyGath.StrategyGath import Base_Strategy_Group

from CommIf.SysFile import Base_File_Oper
from CommIf.CodeTable import ManageCodeTable
from CommIf.CodePool import ManageSelfPool
from CommIf.PrintLog import SysLogIf, PatLogIf

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class UserFrame(wx.Frame):

    def __init__(self, parent=None, id=-1, displaySize=(1600, 900), Fun_SwFrame=None):

        # M1 与 M2 横向布局时宽度分割
        self.M1_width = int(displaySize[0] * 0.1)
        self.M2_width = int(displaySize[0] * 0.9)
        # M1 纵向100%
        self.M1_length = int(displaySize[1])

        # M1中S1 S2 S3 纵向布局高度分割
        self.M1S1_length = int(self.M1_length * 0.2)
        self.M1S2_length = int(self.M1_length * 0.2)
        self.M1S3_length = int(self.M1_length * 0.6)

        # 默认样式wx.DEFAULT_FRAME_STYLE含
        # wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, parent=None, title=u'量化软件', size=displaySize, style=wx.DEFAULT_FRAME_STYLE)

        # 用于量化工具集成到整体系统中
        self.fun_swframe = Fun_SwFrame

        # 多子图布局对象
        self.FlexGridSizer = None

        # 存储单个行情数据
        self.stock_dat = pd.DataFrame()
        # 存储单个回测数据
        self.backt_dat = pd.DataFrame()

        # 存储策略函数
        self.function = ''

        # 初始化事件调用接口
        self.EventHandle = EventHandle()
        self.call_method = self.EventHandle.call_method
        self.event_task = self.EventHandle.event_task

        # 添加参数布局
        self.vbox_sizer_a = wx.BoxSizer(wx.VERTICAL)  # 纵向box
        #self.vbox_sizer_a.Add(self._init_treelist_ctrl(), proportion=3, flag=wx.EXPAND | wx.BOTTOM, border=5)
        self.vbox_sizer_a.Add(self._init_text_log(), proportion=1, flag=wx.EXPAND | wx.BOTTOM, border=5)
        self.vbox_sizer_a.Add(self._init_listbox_mult(), proportion=1, flag=wx.EXPAND | wx.BOTTOM, border=5)
        self.vbox_sizer_a.Add(self._init_nav_notebook(), proportion=2, flag=wx.EXPAND | wx.BOTTOM, border=5)

        #self.vbox_sizer_a.Add(self._init_grid_pl(), proportion=5, flag=wx.EXPAND | wx.BOTTOM, border=5)

        # 加载配置文件
        firm_para = Base_File_Oper.load_sys_para("firm_para.json")
        back_para = Base_File_Oper.load_sys_para("back_para.json")

        # 创建显示区面板
        self.DispPanel = Sys_Panel(self, **firm_para['layout_dict']) # 自定义
        self.BackMplPanel = Sys_Panel(self, **back_para['layout_dict']) # 自定义
        self.DispPanelA = self.DispPanel

        # 此处涉及windows和macos的区别
        sys_para = Base_File_Oper.load_sys_para("sys_para.json")
        if sys_para["operate_sys"] == "windows":
            try:
                # WIN环境下兼容WEB配置
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                     r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_BROWSER_EMULATION",
                                     0, winreg.KEY_ALL_ACCESS)  # 打开所有权限
                # 设置注册表python.exe 值为 11000(IE11)
                winreg.SetValueEx(key, 'python.exe', 0, winreg.REG_DWORD, 0x00002af8)
            except:
                # 设置出现错误
                MessageDialog("WIN环境配置注册表中浏览器兼容显示出错,检查是否安装第三方库【winreg】")

        # 创建wxGrid表格对象
        self._init_grid_pk()
        # 创建text日志对象
        self._init_patten_log()

        # 第二层布局
        self.vbox_sizer_b = wx.BoxSizer(wx.VERTICAL)  # 纵向box
        self.vbox_sizer_b.Add(self._init_para_notebook(), proportion=1, flag=wx.EXPAND | wx.BOTTOM, border=5)  # 添加行情参数布局
        self.vbox_sizer_b.Add(self.patten_log_tx, proportion=10, flag=wx.EXPAND | wx.BOTTOM, border=5)

        # 第一层布局
        self.HBoxPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.HBoxPanelSizer.Add(self.vbox_sizer_a, proportion=1, border=2, flag=wx.EXPAND | wx.ALL)
        self.HBoxPanelSizer.Add(self.vbox_sizer_b, proportion=10, border=2, flag=wx.EXPAND | wx.ALL)
        self.SetSizer(self.HBoxPanelSizer)  # 使布局有效

        # 初始化全部页面
        self.switch_main_panel(self.patten_log_tx, self.grid_pk, False)
        self.switch_main_panel(self.grid_pk, self.BackMplPanel, False)
        self.switch_main_panel(self.BackMplPanel, self.DispPanel, True)  # 等类型替换

        ################################### 辅助配置 ###################################
        self.syslog = SysLogIf(self.sys_log_tx)
        self.patlog = PatLogIf(self.patten_log_tx)

        #self.timer = wx.Timer(self)  # 创建定时器
        #self.Bind(wx.EVT_TIMER, self.ev_int_timer, self.timer)  # 绑定一个定时器事件

        ################################### 变量初始化 ###################################
        self.failed_list = [] # 更新失败列表

        self.start_time = time.perf_counter()
        self.elapsed_time = time.perf_counter()
        self.dialog = None

        ################################### 加载股票代码表 ###################################
        self.code_table = ManageCodeTable(self.syslog)
        self.code_table.update_stock_code()

        # 获取股票代码
        self.stock_list_all = self.code_table.stock_codes.values() #df_basic.ts_code.values
        self.stock_tree_info = dict(zip(self.code_table.stock_codes.values(), self.code_table.stock_codes.keys()))
        self.total_len = len(self.stock_list_all)
        self.treeListStock.refDataShow(self.stock_tree_info) # TreeCtrl显示数据接口

        ################################### 加载自选股票池 ###################################
        self.self_pool = ManageSelfPool(self.syslog)
        self.grid_pl.SetTable(self.self_pool.load_self_pool(), ["自选股", "代码"])

        self._init_status_bar()
        self._init_menu_bar()

    def _init_treelist_strategy(self, subpanel):

        # 创建一个 treeListCtrl object
        self.treeListStgy = CollegeTreeListCtrl(parent=subpanel, pos=(-1, 39), size=(250, 200))
        self.treeListStgy.Bind(wx.EVT_TREE_SEL_CHANGED, self._ev_click_on_treelist)

        return self.treeListStgy

    def _init_treelist_stock(self, subpanel):

        data_path  = os.path.dirname(os.path.dirname(__file__)) + '/DataFiles/stock_history/'
        self.treeListStock = CollegeTreeListCtrl2(parent=subpanel, store_path=data_path, size=(200, 400))
        self.treeListStock.Bind(wx.EVT_TREE_SEL_CHANGED, self._ev_OnTreeListCtrlClickFunc)

        return self.treeListStock

    def _init_nav_notebook(self):

        # 创建参数区面板
        self.NavNoteb = wx.Notebook(self)

        self.NavNoteb.AddPage(self._init_treelist_strategy(self.NavNoteb), "策略导航")
        self.NavNoteb.AddPage(self._init_treelist_stock(self.NavNoteb), "股票源索引")
        self.NavNoteb.AddPage(self._init_grid_pl(self.NavNoteb), "股票池索引")

        return self.NavNoteb

    def _init_para_notebook(self):

        # 创建参数区面板
        self.ParaNoteb = wx.Notebook(self)
        self.ParaStPanel = wx.Panel(self.ParaNoteb, -1) # 行情
        self.ParaBtPanel = wx.Panel(self.ParaNoteb, -1) # 回测 back test
        self.ParaPtPanel = wx.Panel(self.ParaNoteb, -1) # 条件选股 pick stock
        self.ParaPaPanel = wx.Panel(self.ParaNoteb, -1) # 形态选股 patten

        # 第二层布局
        self.ParaStPanel.SetSizer(self.add_stock_para_lay(self.ParaStPanel))
        self.ParaBtPanel.SetSizer(self.add_backt_para_lay(self.ParaBtPanel))
        self.ParaPtPanel.SetSizer(self.add_pick_para_lay(self.ParaPtPanel))

        self.ParaNoteb.AddPage(self.ParaStPanel, "行情参数")
        self.ParaNoteb.AddPage(self.ParaBtPanel, "回测参数")
        self.ParaNoteb.AddPage(self.ParaPtPanel, "条件选股")

        # 此处涉及windows和macos的区别
        sys_para = Base_File_Oper.load_sys_para("sys_para.json")
        if sys_para["operate_sys"] == "macos":
            self.ParaNoteb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._ev_change_noteb)
        else:
            self.ParaNoteb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._ev_change_noteb)

        return self.ParaNoteb

    def _init_status_bar(self):

        self.statusBar = self.CreateStatusBar() # 创建状态条
        # 将状态栏分割为3个区域,比例为2:1
        self.statusBar.SetFieldsCount(3)
        self.statusBar.SetStatusWidths([-2, -1, -1])
        t = time.localtime(time.time())
        self.SetStatusText("公众号：元宵大师带你用Python量化交易", 0)
        self.SetStatusText("当前版本：%s" % Base_File_Oper.load_sys_para("sys_para.json")["__version__"], 1)
        self.SetStatusText(time.strftime("%Y-%B-%d %I:%M:%S", t), 2)

    def _init_menu_bar(self):

        regMenuInfter = {"&使用帮助": {"&报错排查": self._ev_err_guide_menu, '&实战版介绍': self._ev_funt_guide_menu},
                         "&股票池管理": {"&增量更新股票池": self._ev_code_inc_menu, "&完全替换股票池": self._ev_code_rep_menu},
                         "&主菜单": {"&返回": self._ev_switch_menu}}

        # 创建窗口面板
        menuBar = wx.MenuBar(style=wx.MB_DOCKABLE)

        if isinstance(regMenuInfter, dict):  # 使用isinstance检测数据类型
            for mainmenu, submenus in regMenuInfter.items():
                menuobj = wx.Menu()
                for submenu, funct in submenus.items():
                    subitem = wx.MenuItem(menuobj, wx.ID_ANY, submenu)
                    if funct != None:
                        self.Bind(wx.EVT_MENU, funct, subitem) # 绑定事件
                    menuobj.AppendSeparator()
                    menuobj.Append(subitem)
                menuBar.Append(menuobj, mainmenu)
            self.SetMenuBar(menuBar)

        # 以上代码遍历方式完成以下的内容
        """
        # 返回主菜单按钮
        mainmenu = wx.Menu() 
        backitem = wx.MenuItem(mainmenu, wx.ID_ANY, '&返回')
        self.Bind(wx.EVT_MENU, self._ev_switch_menu, backitem)  # 绑定事件
        mainmenu.Append(backitem)
        menuBar.Append(mainmenu, '&主菜单')
        self.SetMenuBar(menuBar)
        """

    def update_process_bar(self, count):
        self.dialog.Update(self.total_len - count)

    def switch_main_panel(self, org_panel=None, new_panel=None, inplace=True):

        if id(org_panel) != id(new_panel):

            self.vbox_sizer_b.Hide(org_panel)

            if inplace == True:
                self.vbox_sizer_b.Replace(org_panel, new_panel) # 等类型可替换
            else:
                # 先删除后添加
                self.vbox_sizer_b.Detach(org_panel)
                self.vbox_sizer_b.Add(new_panel, proportion=10, flag=wx.EXPAND | wx.BOTTOM, border=5)

            self.vbox_sizer_b.Show(new_panel)
            self.SetSizer(self.HBoxPanelSizer)
            self.HBoxPanelSizer.Layout()

    def _ev_change_noteb(self, event):

        #print(self.ParaNoteb.GetSelection())

        old = event.GetOldSelection()
        new = event.GetSelection()

        sw_obj = [[self.DispPanel, self.FlexGridSizer], self.BackMplPanel, self.grid_pk, self.patten_log_tx]

        if (old >= len(sw_obj)) or (new >= len(sw_obj)):
            raise ValueError(u"切换面板号出错！")

        org_panel = sw_obj[old]
        new_panel = sw_obj[new]

        if (old == 0):
            if self.pick_graph_last != 0:
                org_panel = self.FlexGridSizer
            else:
                org_panel = self.DispPanel

        if new == 0:
            if self.pick_graph_last != 0:
                new_panel = self.FlexGridSizer
            else:
                new_panel = self.DispPanel

        ex_flag = False

        if type(sw_obj[old]) == type(sw_obj[new]): ex_flag = True # 等类型可替换

        self.switch_main_panel(org_panel, new_panel, ex_flag)

    def add_stock_para_lay(self, sub_panel):

        # 行情参数
        stock_para_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 行情参数——输入股票代码
        self.stock_code_box = wx.StaticBox(sub_panel, -1, u'股票代码')
        self.stock_code_sizer = wx.StaticBoxSizer(self.stock_code_box, wx.VERTICAL)
        self.stock_code_input = wx.TextCtrl(sub_panel, -1, "sz.000876", style=wx.TE_PROCESS_ENTER)
        self.stock_code_sizer.Add(self.stock_code_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 行情参数——多子图显示
        self.pick_graph_box = wx.StaticBox(sub_panel, -1, u'多子图显示')
        self.pick_graph_sizer = wx.StaticBoxSizer(self.pick_graph_box, wx.VERTICAL)
        self.pick_graph_cbox = wx.ComboBox(sub_panel, -1, u"未开启",
                                           choices=[u"未开启", u"A股票走势-MPL", u"B股票走势-MPL", u"C股票走势-MPL", u"D股票走势-MPL",
                                                    u"A股票走势-WEB", u"B股票走势-WEB", u"C股票走势-WEB", u"D股票走势-WEB"],
                                           style=wx.CB_READONLY | wx.CB_DROPDOWN)
        self.pick_graph_cbox.SetSelection(0)
        self.pick_graph_last = self.pick_graph_cbox.GetSelection()
        self.pick_graph_sizer.Add(self.pick_graph_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.pick_graph_cbox.Bind(wx.EVT_COMBOBOX, self._ev_select_graph)

        # 行情参数——股票组合分析
        self.group_analy_box = wx.StaticBox(sub_panel, -1, u'投资组合分析')
        self.group_analy_sizer = wx.StaticBoxSizer(self.group_analy_box, wx.VERTICAL)
        self.group_analy_cmbo = wx.ComboBox(sub_panel, -1, u"预留A",
                                             choices=[u"预留A", u"收益率/波动率", u"走势叠加分析", u"财务指标评分-预留"],
                                             style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 策略名称
        self.group_analy_sizer.Add(self.group_analy_cmbo, proportion=0,
                                    flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.group_analy_cmbo.Bind(wx.EVT_COMBOBOX, self._ev_group_analy)  # 绑定ComboBox事件

        # 下载按钮
        self.adv_func_but = wx.Button(sub_panel, -1, "高级功能")
        self.adv_func_but.Bind(wx.EVT_BUTTON, self._ev_adv_func)  # 绑定按钮事件

        stock_para_sizer.Add(self.stock_code_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.pick_graph_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.group_analy_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.adv_func_but, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)

        return stock_para_sizer

    def add_backt_para_lay(self, sub_panel):

        # 回测参数
        back_para_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 行情参数——输入股票代码
        self.backt_code_box = wx.StaticBox(sub_panel, -1, u'股票代码')
        self.backt_code_sizer = wx.StaticBoxSizer(self.backt_code_box, wx.VERTICAL)
        self.backt_code_input = wx.TextCtrl(sub_panel, -1, "sz.000876", style=wx.TE_PROCESS_ENTER)
        self.backt_code_sizer.Add(self.backt_code_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)


        # 回测按钮
        self.start_back_but = wx.Button(sub_panel, -1, "开始回测")
        self.start_back_but.Bind(wx.EVT_BUTTON, self._ev_start_run)  # 绑定按钮事件

        # 交易日志
        self.trade_log_but = wx.Button(sub_panel, -1, "交易日志")
        self.trade_log_but.Bind(wx.EVT_BUTTON, self._ev_trade_log)  # 绑定按钮事件

        back_para_sizer.Add(self.backt_code_sizer, proportion=0, flag=wx.EXPAND|wx.ALL|wx.CENTER, border=10)
        back_para_sizer.Add(self.start_back_but, proportion=0, flag=wx.EXPAND|wx.ALL|wx.CENTER, border=10)
        back_para_sizer.Add(self.trade_log_but, proportion=0, flag=wx.EXPAND|wx.ALL|wx.CENTER, border=10)
        return back_para_sizer

    def add_pick_para_lay(self, sub_panel):

        # 选股参数
        pick_para_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 选股参数——日历控件时间周期
        self.dpc_cur_time = wx.adv.DatePickerCtrl(sub_panel, -1,
                                                  style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)  # 当前时间

        self.cur_date_box = wx.StaticBox(sub_panel, -1, u'当前日期(Start)')
        self.cur_date_sizer = wx.StaticBoxSizer(self.cur_date_box, wx.VERTICAL)
        self.cur_date_sizer.Add(self.dpc_cur_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        date_time_now = wx.DateTime.Now()  # wx.DateTime格式"03/03/18 00:00:00"
        self.dpc_cur_time.SetValue(date_time_now)
        # self.dpc_cur_time.SetValue(date_time_now.SetDay(9)) # 以9日为例 先不考虑周末的干扰

        # 选股参数——条件表达式分析
        self.pick_stock_box = wx.StaticBox(sub_panel, -1, u'条件表达式选股')
        self.pick_stock_sizer = wx.StaticBoxSizer(self.pick_stock_box, wx.HORIZONTAL)

        self.pick_item_cmbo = wx.ComboBox(sub_panel, -1,  choices=[],
                                            style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 选股项
        self.pick_item_cmbo.Bind(wx.EVT_RADIOBUTTON, self._ev_items_choose)


        self.pick_cond_cmbo = wx.ComboBox(sub_panel, -1, u"大于",
                                          choices=[u"大于", u"等于", u"小于"],
                                          style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 选股条件
        self.pick_value_text = wx.TextCtrl(sub_panel, -1, "0", style=wx.TE_LEFT)

        self.sort_values_cmbo = wx.ComboBox(sub_panel, -1, u"不排列",
                                            choices=[u"不排列", u"升序", u"降序"],
                                            style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 排列条件

        self.pick_stock_sizer.Add(self.pick_item_cmbo, proportion=0,
                                  flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.pick_stock_sizer.Add(self.pick_cond_cmbo, proportion=0,
                                  flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.pick_stock_sizer.Add(self.pick_value_text, proportion=0,
                                  flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.pick_stock_sizer.Add(self.sort_values_cmbo, proportion=0,
                                  flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 子参数——剔除ST/*ST 及 标记自选股
        self.adv_select_box = wx.StaticBox(sub_panel, -1, u'勾选确认')
        self.adv_select_sizer = wx.StaticBoxSizer(self.adv_select_box, wx.HORIZONTAL)
        self.mark_self_chk = wx.CheckBox(sub_panel, label='标记自选股')
        self.mark_self_chk.Bind(wx.EVT_CHECKBOX, self._ev_mark_self)  # 绑定复选框事件

        self.remove_st_chk = wx.CheckBox(sub_panel, label='剔除ST/*ST')
        self.adv_select_sizer.Add(self.mark_self_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.adv_select_sizer.Add(self.remove_st_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)


        """
        self.src_dat_radio = wx.RadioBox(sub_panel, -1, label=u'数据源选取', choices=["tushare每日指标","离线每日指标"],
                                         majorDimension = 2, style = wx.RA_SPECIFY_ROWS)
        """

        # 选股序列按钮——刷新数据 + 开始选股 + 保存结果
        self.start_pick_but = wx.Button(sub_panel, -1, "选股过程")
        self.start_pick_but.Bind(wx.EVT_BUTTON, self._ev_select_seq)  # 绑定按钮事件

        pick_para_sizer.Add(self.cur_date_sizer, proportion=0, flag=wx.EXPAND | wx.ALL| wx.CENTER, border=10)
        pick_para_sizer.Add(self.pick_stock_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        pick_para_sizer.Add(self.adv_select_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        pick_para_sizer.Add(self.start_pick_but, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)

        return pick_para_sizer

    def _init_grid_pk(self):
        # 初始化选股表格
        self.grid_pk = GridTable(parent=self)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self._ev_cell_lclick_pkcode, self.grid_pk)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self._ev_label_lclick_pkcode, self.grid_pk)

        self.df_use = pd.DataFrame()
        self.filte_result = pd.DataFrame()
        return self.grid_pk

    def _init_patten_log(self):

        # 创建形态选股日志
        self.patten_log_tx = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(250, 300))

        return self.patten_log_tx

    def _init_grid_pl(self, subpanel):
        # 初始化股票池表格
        self.grid_pl = GridTable(parent=subpanel, nrow=0, ncol=2)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self._ev_click_plcode, self.grid_pl)
        return self.grid_pl

    def _init_listbox_mult(self):

        self.mult_analyse_box = wx.StaticBox(self, -1, u'组合分析股票池')
        self.mult_analyse_sizer = wx.StaticBoxSizer(self.mult_analyse_box, wx.VERTICAL)
        self.listBox = wx.ListBox(self, -1, size=(self.M1_width, self.M1S2_length), choices=[], style=wx.LB_EXTENDED)
        self.listBox.Bind(wx.EVT_LISTBOX_DCLICK, self._ev_list_select)
        self.mult_analyse_sizer.Add(self.listBox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        return self.mult_analyse_sizer

    def _init_text_log(self):

        # 创建并初始化系统日志框
        self.sys_log_box = wx.StaticBox(self, -1, u'系统日志')
        self.sys_log_sizer = wx.StaticBoxSizer(self.sys_log_box, wx.VERTICAL)
        self.sys_log_tx = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(self.M1_width, self.M1S1_length))
        self.sys_log_sizer.Add(self.sys_log_tx, proportion=1, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        return self.sys_log_sizer

    def refresh_grid(self, df, back_col=""):
        self.grid_pk.SetTable(df, self.tran_col)
        self.grid_pk.SetSelectCol(back_col)

    def refresh_grid1(self, update_df):

        self.grid.Destroy()  # 先摧毁 后创建
        self.data_to_grid(update_df)

        self.HBoxPanelSizer.Add(self.grid, proportion=10, border=2, flag=wx.EXPAND | wx.ALL)
        self.SetSizer(self.HBoxPanelSizer)  # 使布局有效
        self.HBoxPanelSizer.Layout()

    def _ev_select_graph(self, event):

        item = event.GetSelection()

        # 显示区一级切换
        if item != 0 and self.pick_graph_last == 0: # 单图切到多子图

            if item <= 4: # 1-4 属于MPL显示区
                self.graphs_obj = SubGraphs(self)
            elif item <= 8: # 5-8 属于WEB显示区
                self.graphs_obj = WebGraphs(self)
            else: # 故障保护
                MessageDialog("一级切换-0错误！")
                self.graphs_obj = SubGraphs(self)
            self.switch_main_panel(self.DispPanel, self.graphs_obj.FlexGridSizer, False)
            self.FlexGridSizer = self.graphs_obj.FlexGridSizer

        elif item == 0 and self.pick_graph_last != 0: # 多子图切到单图
            #print(self.vbox_sizer_b.GetItem(self.DispPanel))
            self.switch_main_panel(self.FlexGridSizer, self.DispPanel, False)

        elif item <= 4 and self.pick_graph_last > 4:
            self.graphs_obj = SubGraphs(self)
            self.switch_main_panel(self.FlexGridSizer, self.graphs_obj.FlexGridSizer, True)
            self.FlexGridSizer = self.graphs_obj.FlexGridSizer

        elif item > 4 and self.pick_graph_last <= 4:
            self.graphs_obj = WebGraphs(self)
            self.switch_main_panel(self.FlexGridSizer, self.graphs_obj.FlexGridSizer, True)
            self.FlexGridSizer = self.graphs_obj.FlexGridSizer
        else:
            pass

        # 显示区二级切换
        if item == 1 or item == 5:
            self.DispPanelA = self.graphs_obj.DispPanel0
            #self.ochl = self.DispPanel0.ochl
            #self.vol = self.DispPanel0.vol
        elif item == 2 or item == 6:
            self.DispPanelA = self.graphs_obj.DispPanel1
            #self.ochl = self.DispPanel1.ochl
            #self.vol = self.DispPanel1.vol
        elif item == 3 or item == 7:
            self.DispPanelA = self.graphs_obj.DispPanel2
            #self.ochl = self.DispPanel2.ochl
            #self.vol = self.DispPanel2.vol
        elif item == 4 or item == 8:
            self.DispPanelA = self.graphs_obj.DispPanel3
            #self.ochl = self.DispPanel3.ochl
            #self.vol = self.DispPanel3.vol
        else:
            self.DispPanelA = self.DispPanel

        self.pick_graph_last = item

    def _ev_select_seq(self, event):

        select_msg = ChoiceDialog(u"选股流程点击处理事件",  [u"第一步:刷新选股数据",
                                                        u"第二步:开始条件选股",
                                                        u"第三步:保存选股结果"])

        if select_msg == u"第一步:刷新选股数据":
            self._download_st_data()

        elif select_msg == u"第二步:开始条件选股":
            self._start_st_slect()

        elif select_msg == u"第三步:保存选股结果":
            self._save_st_result()

        else:
            pass

    def _start_st_slect(self):

        if self.df_use.empty == True:
            MessageDialog("请先获取选股数据！")
            return

        if self.mark_self_chk.GetValue() == True:  # 复选框被选中
            MessageDialog("先取消复选框！！！")
            return

        if self.remove_st_chk.GetValue() == True:  # 剔除ST/*ST

            self.df_use.dropna(subset=['股票名称'], inplace=True)
            self.df_use = self.df_use[self.df_use['股票名称'].apply(lambda x: x.find('ST') < 0)]

        val = self.pick_item_cmbo.GetStringSelection()  # 获取当前选股combox的选项

        if val in self.df_use.columns.tolist():  # DataFrame中是否存在指标

            para_value = self.pick_value_text.GetValue()

            if val in [u"股票代码", u"所属行业", u"股票名称"]:
                # 字符串type
                para_values = str(self.pick_value_text.GetValue())

                if self.pick_cond_cmbo.GetStringSelection() == u"等于":
                    self.filte_result = pd.DataFrame()
                    for value in para_values.split("|"):  # 支持用"｜"符号查询多个
                        self.filte_result = pd.concat([self.filte_result, self.df_use[self.df_use[val] == value]])
                else:
                    MessageDialog("【%s】选项只支持【等于】条件判断！！！" % (val))
                    return

            if self.pick_cond_cmbo.GetStringSelection() == u"大于":
                self.filte_result = self.df_use[self.df_use[val] > float(para_value)]
            elif self.pick_cond_cmbo.GetStringSelection() == u"小于":
                self.filte_result = self.df_use[self.df_use[val] < float(para_value)]
            elif self.pick_cond_cmbo.GetStringSelection() == u"等于":
                self.filte_result = self.df_use[self.df_use[val] == para_value]
            else:
                pass

            if self.sort_values_cmbo.GetStringSelection() == u"降序":
                self.filte_result.sort_values(by=val, axis='index', ascending=False, inplace=True,
                                              na_position='last')
            elif self.sort_values_cmbo.GetStringSelection() == u"升序":
                self.filte_result.sort_values(by=val, axis='index', ascending=True, inplace=True,
                                              na_position='last')
            else:
                pass

            if self.filte_result.empty != True:

                ser_col = self.filte_result[val]  # 先单独保存
                self.filte_result.drop(val, axis=1, inplace=True)  # 而后从原数据中删除
                self.filte_result.insert(0, val, ser_col)  # 插入至首个位置

                self.df_use = self.filte_result
                self.refresh_grid(self.filte_result, val)
            else:
                MessageDialog("未找到符合条件的数据！！！")

    def _download_st_data(self): # 复位选股按钮事件

        if self.mark_self_chk.GetValue() == True: # 复选框被选中
            MessageDialog("先取消复选框！！！")
            return

        sdate_obj = self.dpc_cur_time.GetValue()
        sdate_val = datetime(sdate_obj.year, sdate_obj.month + 1, sdate_obj.day)

        select_src = ChoiceDialog(u"选股数据源选取", [u"爬虫每日指标",
                                                    u"基金季度持仓",
                                                    u"离线业绩预告"])
        if select_src == "tushare每日指标":

            # 组合加入tushare数据
            self.ts_data = Tspro_Backend()
            self.df_join = self.ts_data.datafame_join(sdate_val.strftime('%Y%m%d'))  # 刷新self.df_join

        elif select_src == "爬虫每日指标":

            dlg_mesg = wx.SingleChoiceDialog(None, "刷新股票池 或者 刷新数据源？",
                                             u"刷新类别选择", ['A股数据源', '自选股票池'])
            dlg_mesg.SetSelection(0)  # default selection

            if dlg_mesg.ShowModal() == wx.ID_OK:
                message = dlg_mesg.GetStringSelection()
                dlg_mesg.Destroy()

                self.ts_data = CrawerDailyBackend(self.syslog)
                self.df_join = self.ts_data.datafame_join(sdate_val.strftime('%Y%m%d'))  # 刷新self.df_join

                if message == '自选股票池':
                    df_pool = pd.DataFrame()
                    for sub_dict in self.self_pool.load_pool_stock().values():
                        num, sym = sub_dict.upper().split(".")
                        code = sym + "." + num
                        df_pool = df_pool.append(self.df_join[self.df_join["股票代码"] == code],
                                                           ignore_index=True)
                    self.df_join = df_pool


        elif select_src == "基金季度持仓":

            MessageDialog("2.1.study 未开放该功能！")
            return

        else: # 离线csv文件
            # 第一步:收集导入文件路径
            get_path = ImportFileDiag()

            if get_path != '':
                # 组合加入tushare数据
                self.ts_data = Csv_Backend(select_src)
                self.df_join = self.ts_data.load_pick_data(get_path)
            else:
                self.df_join = pd.DataFrame()

        if self.df_join.empty == True:
            MessageDialog("选股数据为空！请检查数据源是否有效！\n")
        else:
            # 数据获取正常后执行

            self.filter = self.df_join.columns.tolist()
            self.tran_col = dict(zip(self.df_join.columns.tolist(), self.filter))

            self.pick_item_cmbo.Clear()
            self.pick_item_cmbo.Append(self.filter)
            self.pick_item_cmbo.SetValue(self.filter[0])

            self.df_use = self.df_join
            self.refresh_grid(self.df_use, self.df_use.columns.tolist()[0])

            if select_src == "爬虫接口获取":

                if select_msg == u"爬虫每日指标":
                    if MessageDialog('是否查看Web版【板块-个股-涨跌幅】集合') == "点击Yes":
                        MessageDialog("2.1.study 未开放该功能！")
                        return


    def _save_st_result(self):
        # 保存选股按钮事件

        st_name_code_dict = dict(zip(self.df_use["股票名称"].values, self.df_use["股票代码"].values))

        choice_msg = ChoiceDialog("保存条件筛选后的股票", [u"完全替换", u"增量更新"])

        if choice_msg == u"完全替换":
            self.self_pool.update_replace_st(st_name_code_dict)
        elif choice_msg == u"增量更新":
            self.self_pool.update_increase_st(st_name_code_dict)
        else:
            pass
        self.grid_pl.SetTable(self.self_pool.load_self_pool(), ["自选股", "代码"])
        #self.df_use.to_csv('table-stock.csv', columns=self.df_use.columns, index=True, encoding='GB18030')

    def _ev_mark_self(self, event):
        # 标记自选股事件

        if self.df_use.empty == True:
            MessageDialog("无选股数据！")
        else:
            self.df_use.reset_index(drop=True, inplace=True) # 重排索引

            if self.mark_self_chk.GetValue() == True: # 复选框被选中

                for code in list(self.self_pool.load_pool_stock().values()): # 加载自选股票池
                    symbol, number = code.upper().split('.')
                    new_code = number + "." + symbol
                    n_list = self.df_use[self.df_use["股票代码"] == new_code].index.tolist()
                    if n_list != []:
                        self.grid_pk.SetCellBackgroundColour(n_list[0], 0, wx.YELLOW)
                        self.grid_pk.SetCellBackgroundColour(n_list[0], 1, wx.YELLOW)
            else:
                for code in list(self.self_pool.load_pool_stock().values()): # 加载自选股票池
                    symbol, number = code.upper().split('.')
                    new_code = number + "." + symbol
                    n_list = self.df_use[self.df_use["股票代码"] == new_code].index.tolist()
                    if n_list != []:
                        self.grid_pk.SetCellBackgroundColour(n_list[0], 0, wx.WHITE)
                        self.grid_pk.SetCellBackgroundColour(n_list[0], 1, wx.WHITE)
            self.grid_pk.Refresh()

    def _ev_trade_log(self, event):

        user_trade_log = UserDialog(self, title=u"回测提示信息", label=u"交易详细日志")

        """ 自定义提示框 """
        if user_trade_log.ShowModal() == wx.ID_OK:
            pass
        else:
            pass

    def _ev_click_on_treelist(self, event):

        self.curTreeItem = self.treeListStgy.GetItemText(event.GetItem())

        if self.curTreeItem != None:
            # 当前选中的TreeItemId对象操作

            if MessageDialog('当前点击:{0}!'.format(self.curTreeItem))!= "点击Yes":
                return
            for m_key, m_val in self.treeListStgy.colleges.items():
                for s_key in m_val:
                    if s_key.get('名称', '') == self.curTreeItem:
                        if s_key.get('函数', '') != "未定义":
                            if (m_key == u"衍生指标") or (m_key == u"K线形态"):
                                # 第一步:收集控件中设置的选项
                                st_label = s_key['标识']

                                ochl_paras = MarketGraphDialog(self, "行情走势参数配置")

                                # 第一步:收集控件中设置的选项
                                if ochl_paras.ShowModal() != wx.ID_OK:
                                    return
                                else:
                                    st_paras = ochl_paras.feedback_paras()

                                choice_msg = ChoiceDialog("择时策略作用范围", [u"指定个股", u"自选股票池"])

                                if choice_msg == u"指定个股":
                                    st_code = self.stock_code_input.GetValue()
                                    st_name = self.code_table.get_name(st_code)

                                    self.stock_dat = self.requset_stock_dat(st_code, st_name,
                                                                            st_paras["股票周期"], st_paras["股票复权"],
                                                                            st_paras["开始日期"], st_paras["结束日期"])

                                    # 第二步:获取股票数据-使用self.stock_dat存储数据
                                    if self.stock_dat.empty == True:
                                        MessageDialog("获取股票数据出错！\n")
                                    else:
                                        # 第三步:绘制可视化图形
                                        if self.pick_graph_cbox.GetSelection() != 0:
                                            self.DispPanelA.clear_subgraph()  # 必须清理图形才能显示下一幅图
                                            self.DispPanelA.draw_subgraph(self.stock_dat, st_code,
                                                                          st_paras["股票周期"] + st_paras["股票复权"])
                                        else:
                                            # 配置图表属性
                                            firm_para = self.call_method(self.event_task['cfg_firm_para'],
                                                                         st_code=st_code,
                                                                         st_name=st_name,
                                                                         st_period=st_paras["股票周期"],
                                                                         st_auth=st_paras["股票复权"],
                                                                         st_label=st_label)

                                            self.DispPanelA.firm_graph_run(self.stock_dat, **firm_para)
                                        self.DispPanelA.update_subgraph()  # 必须刷新才能显示下一幅图

                                elif choice_msg == u"自选股票池":
                                    user_trade_log = ScanDialog(self, st_label, self.self_pool.load_pool_stock(),
                                                                 st_paras["股票周期"], st_paras["股票复权"],
                                                                 st_paras["开始日期"], st_paras["结束日期"],
                                                                 title=u"扫描自选股票池择时信号", label=u"信号生成明细")
                                    user_trade_log.Show()
                                else:
                                    return
                            else:
                                self.function = getattr(Base_Strategy_Group, s_key.get('define', ''))
                        else:
                            MessageDialog("该接口未定义！")
                        break

    ################################### 事件函数 ###################################
    def _ev_OnTreeListCtrlClickFunc(self, event):
        self.currentTreeItem = self.treeListStock.GetItemText(event.GetItem())

        try:
            df = pd.read_csv(data_path + self.currentTreeItem, index_col=0, parse_dates=[u"日期"], encoding='GBK',
                             engine='python')  # 文件名中含有中文时使用engine为python

            view_stock_data = ViewGripDiag(self, u"查看离线日线数据csv", df)
            """ 自定义提示框 """
            if view_stock_data.ShowModal() == wx.ID_OK:
                pass
            else:
                pass

        except:
            MessageDialog("读取文件出错! \n")

    def _ev_start_run(self, event): # 点击运行回测

        # 第一步:收集控件中设置的选项
        st_code = self.stock_code_input.GetValue()
        st_name = self.code_table.get_name(st_code)
        backt_paras = BacktGraphDialog(self, "回测参数配置")
        backt_paras.Centre()
        # 第一步:收集控件中设置的选项
        if backt_paras.ShowModal() != wx.ID_OK:
            return
        else:
            bt_paras = backt_paras.feedback_paras()


        # 第二步:获取股票数据-依赖行情界面获取的数据
        self.backt_dat = self.requset_stock_dat(st_code,  st_name,
                                                bt_paras["股票周期"], bt_paras["股票复权"],
                                                bt_paras["开始日期"], bt_paras["结束日期"])

        if self.backt_dat.empty == True:
            MessageDialog("获取回测数据出错！\n")
            return

        if self.function == '':
            MessageDialog("未选择回测策略！")
            return

        # 第三步:绘制可视化图形
        # 配置图表属性
        back_para = self.call_method(self.event_task['cfg_back_para'],
                                     st_code=st_code,
                                     cash_value=bt_paras[u"初始资金"],
                                     stake_value=bt_paras[u"交易规模"],
                                     slippage_value=bt_paras[u"滑点"],
                                     commission_value=bt_paras[u"手续费"],
                                     tax_value=bt_paras[u"印花税"])

        self.BackMplPanel.back_graph_run(self.function(self.backt_dat), **back_para)
        # 修改图形的任何属性后都必须更新GUI界面
        self.BackMplPanel.update_subgraph()

    def requset_stock_dat(self, st_code, st_name, st_period, st_auth, sdate_obj, edate_obj):

        # 第二步:获取股票数据-调用sub event handle
        stock_dat = self.call_method(self.event_task['get_stock_dat'],
                                          st_code=st_code,
                                          st_period=st_period,
                                          st_auth=st_auth,
                                          sdate_obj=sdate_obj,
                                          edate_obj=edate_obj)
        return stock_dat

    def handle_active_code(self, st_code, st_name): # 点击股票代码后处理模块

        select_msg = ChoiceDialog(u"自选股点击处理事件",  [u"从股票池中剔除",
                                                        u"加入组合分析池",
                                                        u"查看行情走势",
                                                        u"查看F10资料",
                                                        u"K线自动播放",
                                                        u"导入离线数据"
                                                        ])

        if select_msg == u"查看行情走势":

            ochl_paras = MarketGraphDialog(self, "行情走势参数配置")
            ochl_paras.Centre()
            # 第一步:收集控件中设置的选项
            if ochl_paras.ShowModal() != wx.ID_OK:
                return
            else:
                st_paras = ochl_paras.feedback_paras()

            self.stock_dat = self.requset_stock_dat(st_code,  st_name,
                                                    st_paras["股票周期"], st_paras["股票复权"],
                                                    st_paras["开始日期"], st_paras["结束日期"])

            if self.stock_dat.empty == True:
                MessageDialog("获取股票数据出错！\n")
            else:

                if len(self.stock_dat) >= 356:
                    MessageDialog("获取股票数据量较大！默认显示最近的365个BAR数据！\n")
                    self.stock_dat = self.stock_dat[-356:]

                # 第三步:绘制可视化图形
                if self.pick_graph_cbox.GetSelection() != 0:
                    self.DispPanelA.clear_subgraph()  # 必须清理图形才能显示下一幅图
                    self.DispPanelA.draw_subgraph(self.stock_dat, st_code, st_paras["股票周期"] + st_paras["股票复权"])

                else:
                    # 配置图表属性
                    firm_para = self.call_method(self.event_task['cfg_firm_para'],
                                                 st_code=st_code,
                                                 st_name=st_name,
                                                 st_period=st_paras["股票周期"],
                                                 st_auth=st_paras["股票复权"])

                    self.DispPanelA.firm_graph_run(self.stock_dat, **firm_para)

                self.DispPanelA.update_subgraph()  # 必须刷新才能显示下一幅图

        elif select_msg == u"加入组合分析池":
            self._add_analyse_list(st_code+"|"+st_name)

        elif select_msg == u"从股票池中剔除":
            self.self_pool.delete_one_st(st_name)
            self.grid_pl.SetTable(self.self_pool.load_self_pool(), ["自选股", "代码"])

        elif select_msg == u"查看F10资料":
            MessageDialog("2.1.study 未开放该功能！")
            return

        elif select_msg == u"K线自动播放":
            MessageDialog("2.1.study 未开放该功能！")
            return

        elif select_msg == u"导入离线数据":

            if MessageDialog("请手动填写[股票名称][股票周期][股票复权]！\n该内容与图表标签相关！\n点击Yes继续；点击No去配置") == "点击No":
                return

            # 第一步:收集导入文件路径/名称/周期/起始时间
            get_path = ImportFileDiag()
            st_code = self.stock_code_input.GetValue()
            st_name = self.code_table.get_name(st_code)

            ochl_paras = MarketGraphDialog(self, "行情走势参数配置")
            ochl_paras.Centre()
            # 第一步:收集控件中设置的选项
            if ochl_paras.ShowModal() != wx.ID_OK:
                return
            else:
                st_paras = ochl_paras.feedback_paras()

            # 第二步:加载csv文件中的数据
            if get_path != '':
                self.stock_dat = self.call_method(self.event_task['get_csvst_dat'],
                                                  get_path=get_path,
                                                  sdate_obj=st_paras["开始日期"], edate_obj=st_paras["结束日期"],
                                                  st_auth=st_paras["股票复权"], st_period=st_paras["股票周期"])

                if self.stock_dat.empty == True:
                    MessageDialog("文件内容为空！\n")
                else:

                    # 第三步:绘制可视化图形
                    if self.pick_graph_cbox.GetSelection() != 0:
                        self.DispPanelA.clear_subgraph()  # 必须清理图形才能显示下一幅图
                        self.DispPanelA.draw_subgraph(self.stock_dat, "csv导入" + st_code, st_name)
                    else:
                        # 配置图表属性
                        firm_para = self.call_method(self.event_task['cfg_firm_para'],
                                                     st_code="csv导入" + st_code,
                                                     st_name=st_name,
                                                     st_period=st_paras["股票周期"],
                                                     st_auth="不复权")
                        self.DispPanelA.firm_graph_run(self.stock_dat, **firm_para)
                    self.DispPanelA.update_subgraph()  # 必须刷新才能显示下一幅图
        else:
            pass

    def _ev_click_plcode(self, event):  # 点击股票池股票代码

        # 收集股票池中名称和代码
        st_code = self.grid_pl.GetCellValue(event.GetRow(), 1)
        st_name = self.grid_pl.GetCellValue(event.GetRow(), 0)

        self.handle_active_code(st_code, st_name)

    def _ev_label_lclick_pkcode(self, event):

        # 收集表格中的列名
        col_label = self.grid_pk.GetColLabelValue(event.GetCol())

        if col_label == "所属行业" and self.src_dat_cmbo.GetStringSelection() == "离线财务报告":

            if MessageDialog("是否对比个股业绩报告？建议同行业板块对比！") == "点击Yes":

                if self.df_use.empty != True:

                    self.df_use.dropna(how='all', axis=1, inplace=True)
                    self.df_use.fillna(0, inplace = True)
                    self.df_use = self.df_use.assign(总分 = 0)

                    for col, series in self.df_use.iteritems():

                        if series.dtype == float and col != "总分":
                            self.df_use[col] = (series - series.mean())/series.var()
                            self.df_use.loc[:,"总分"] += self.df_use[col]

                    self.df_use.sort_values(by=["总分"], axis='index', ascending=False, inplace=True,
                                              na_position='last') # 降序

                    text = "对比后排名前五名单如下:\n"
                    updat_dict = {}
                    for name, code in zip(self.df_use["股票名称"][0:5], self.df_use["股票代码"][0:5]):
                        code = code[1:-1]
                        text += name + "|" + code + "\n"
                        updat_dict.update({name: self.code_table.conv_code(code)})

                    if MessageDialog(text+"\n添加股票到自选股票池？") == "点击Yes":
                        # 自选股票池 更新股票
                        self.self_pool.update_increase_st(updat_dict)
                        self.grid_pl.SetTable(self.self_pool.load_self_pool(), ["自选股", "代码"])

    def _ev_cell_lclick_pkcode(self, event):  # 点击选股表中股票代码

        # 收集表格中的列名
        col_label = self.grid_pk.GetColLabelValue(event.GetCol())

        if col_label == "股票代码":
            # 收集表格中的单元格

            try:
                st_code = self.grid_pk.GetCellValue(event.GetRow(), event.GetCol())
                st_name = self.code_table.get_name(st_code)

                text = self.call_method(self.event_task['get_cash_flow'], st_code=self.code_table.conv_code(st_code))

                if MessageDialog(text+"\n添加股票[%s]到自选股票池？"%(self.code_table.conv_code(st_code) + "|" + st_name)) == "点击Yes":
                    #self._add_analyse_list(self.code_table.conv_code(st_code) + "|" + st_name)
                    # 自选股票池 更新股票
                    self.self_pool.update_increase_st({st_name:self.code_table.conv_code(st_code)})
                    self.grid_pl.SetTable(self.self_pool.load_self_pool(), ["自选股", "代码"])
            except:
                MessageDialog("股票代码不在存储表中！检查是否为新股/退市等情况！")

        elif col_label == "股票名称":
            # 收集表格中的单元格
            try:
                st_name = self.grid_pk.GetCellValue(event.GetRow(), event.GetCol())
                st_code = self.code_table.get_code(st_name)

                text = self.call_method(self.event_task['get_cash_flow'], st_code=self.code_table.conv_code(st_code))

                if MessageDialog(
                        text + "\n添加股票[%s]到自选股票池？" % (self.code_table.conv_code(st_code) + "|" + st_name)) == "点击Yes":
                    # self._add_analyse_list(self.code_table.conv_code(st_code) + "|" + st_name)
                    # 自选股票池 更新股票
                    self.self_pool.update_increase_st({st_name: self.code_table.conv_code(st_code)})
                    self.grid_pl.SetTable(self.self_pool.load_self_pool(), ["自选股", "代码"])
            except:
                MessageDialog("股票名称不在存储表中！检查是否为新股/退市等情况！")

        else:
            MessageDialog("请点击股票代码或股票名称！")

    def _ev_items_choose(self, event):
        pass

    def _ev_list_select(self, event): # 双击从列表中剔除股票

        # 等价与GetSelection() and indexSelected
        if MessageDialog("是否从组合分析股票池中删除该股票？") == "点击Yes":
            indexSelected = event.GetEventObject().GetSelections()
            event.GetEventObject().Delete(indexSelected[0])

    def _ev_group_analy(self, event):

        item = event.GetSelection()
        stock_set = self.listBox.GetStrings()

        ochl_paras = MarketGraphDialog(self, "行情走势参数配置")
        ochl_paras.Centre()
        # 第一步:收集控件中设置的选项
        if ochl_paras.ShowModal() != wx.ID_OK:
            return
        else:
            st_paras = ochl_paras.feedback_paras()

        # 第一步:收集控件中设置的选项
        st_period = st_paras["股票周期"]
        st_auth = st_paras["股票复权"]
        sdate_obj = st_paras["开始日期"]
        edate_obj = st_paras["结束日期"]

        if item == 1: # 显示收益率/波动率分布
            MessageDialog("2.1.study 未开放该功能！")
            return

        elif item == 2:  # 显示走势叠加分析
            MessageDialog("2.1.study 未开放该功能！")
            return

        elif item == 3:  # 显示财务指标评分
            MessageDialog("2.1.study 未开放该功能！")
            return

    def _ev_patten_select(self, event):
        pass

    def _ev_int_timer(self, event):
        pass

    def _ev_switch_menu(self, event):
        self.fun_swframe(0)  # 切换 Frame 主界面

    def _add_analyse_list(self, item):

        if item in self.listBox.GetStrings():
            MessageDialog("股票%s已经存在！\n" % item)
        else:
            self.listBox.InsertItems([item], 0)  # 插入item

    def _ev_err_guide_menu(self, event):
        webbrowser.open('https://blog.csdn.net/hangzhouyx/article/details/113774922?spm=1001.2014.3001.5501')

    def _ev_funt_guide_menu(self, event):
        webbrowser.open('https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzUxMjU4NDAwNA==&action=getalbum&album_id=2524935077060001794#wechat_redirect')

    def _ev_code_inc_menu(self, event):
        # 增量更新
        # 收集导入文件路径
        get_path = ImportFileDiag()

       # 加载csv文件中的数据
        if get_path != '':
            add_code = self.call_method(self.event_task['get_csvst_pool'], get_path=get_path)
            print(add_code)
            if add_code:
                self.self_pool.update_increase_st(add_code)
                self.grid_pl.SetTable(self.self_pool.load_self_pool(), ["自选股", "代码"])
            else:
                MessageDialog("文件内容为空！\n")

    def _ev_code_rep_menu(self, event):
        # 完全替换
        # 收集导入文件路径
        get_path = ImportFileDiag()

       # 加载csv文件中的数据
        if get_path != '':
            add_code = self.call_method(self.event_task['get_csvst_pool'], get_path=get_path)
            if add_code:
                self.self_pool.update_replace_st(add_code)
                self.grid_pl.SetTable(self.self_pool.load_self_pool(), ["自选股", "代码"])
            else:
                MessageDialog("文件内容为空！\n")

    def on_click_start(self, event):
        MessageDialog("2.1.study 未开放该功能！")

    def on_click_fresh(self, event):
        pass

    def on_click_compt(self, event):

        MessageDialog("2.1.study 未开放该功能！")


    def _ev_switch_menu(self, event):
        self.fun_swframe(0)  # 切换 Frame 主界面

    def _patten_urgent_stop(self, cmd="init"):

        if cmd == "init":
            self.pick_patten_but.SetLabel(u"开始选股")
            self.urgent_stop_flag = False
        elif cmd == "wait_stop":
            self.pick_patten_but.SetLabel(u"停止选股")
            self.urgent_stop_flag = False
        elif cmd == "wait_start":
            self.pick_patten_but.SetLabel(u"开始选股")
            self.urgent_stop_flag = True
        else:
            pass

    def _ev_adv_func(self, event):

        # 第一步:收集控件中设置的选项
        st_code = self.stock_code_input.GetValue()
        st_name = self.code_table.get_name(st_code)

        self.handle_active_code(st_code, st_name)

