#! /usr/bin/env python 
#-*- encoding: utf-8 -*- 
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx
import wx.adv
import wx.grid
import wx.html2
import time

from CommIf.SysFile import Base_File_Oper
from MainlyGui.ElementGui.DefDialog import MessageDialog

class ConfFrame(wx.Frame):

    def __init__(self, parent=None, id=-1, displaySize=(1600, 900), Fun_SwFrame=None):

        displaySize_shrink = 0.7*displaySize[0], 0.6*displaySize[1]

        # call base class constructor
        wx.Frame.__init__(self, parent=None, title=u'配置工具', size=displaySize_shrink, style=wx.DEFAULT_FRAME_STYLE)

        # 用于量化工具集成到整体系统中
        self.fun_swframe = Fun_SwFrame

        # 创建菜单栏
        self._init_menu_bar()
        # 创建状态栏
        self._init_status_bar()

        # 加载配置文件
        self.firm_para = Base_File_Oper.load_sys_para("firm_para.json")
        self.back_para = Base_File_Oper.load_sys_para("back_para.json")
        self.sys_para = Base_File_Oper.load_sys_para("sys_para.json")

        # 创建系统参数配置面板
        self.SysPanel = wx.Panel(self, -1)

        sys_input_box = wx.StaticBox(self.SysPanel, -1, u'系统选项')
        sys_input_sizer = wx.StaticBoxSizer(sys_input_box, wx.VERTICAL)

        # 初始化操作系统类别
        self.sel_operate_val = [u"macos", u"windows"]

        self.sel_operate_cmbo = wx.ComboBox(self.SysPanel, -1, self.sys_para["operate_sys"],
                                          choices=self.sel_operate_val,
                                          style=wx.CB_SIMPLE | wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择操作系统
        sel_operate_text = wx.StaticText(self.SysPanel, -1, u'当前操作系统')
        sel_operate_text.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))

        # 界面尺寸大小提示
        disp_size_text = wx.StaticText(self.SysPanel, -1, u'显示器屏幕尺寸：\n长:{};宽:{}'.format(displaySize[0], displaySize[1]))
        disp_size_text.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))

        sys_input_sizer.Add(sel_operate_text, proportion=0, flag=wx.EXPAND | wx.ALL, border=2)
        sys_input_sizer.Add(self.sel_operate_cmbo, 0, wx.EXPAND | wx.ALL | wx.CENTER, 2)
        sys_input_sizer.Add(disp_size_text, 0, wx.EXPAND | wx.ALL | wx.CENTER, 2)

        # 初始化数据存储方式
        data_store_list = [u"本地csv", u"Sqlite"]
        self.data_store_box = wx.RadioBox(self.SysPanel, -1, label=u'数据存储', choices=data_store_list, majorDimension=2,
                                         style=wx.RA_SPECIFY_COLS)
        # 初始化存储变量
        self.data_store_val = self.data_store_box.GetStringSelection()

        # 初始化数据源
        data_src_list = [u"新浪爬虫", u"baostock", u"tushare", u"离线csv"]
        self.data_src_box = wx.RadioBox(self.SysPanel, -1, label=u'数据源', choices=data_src_list,
                                              majorDimension=2, style=wx.RA_SPECIFY_ROWS)
        # 初始化指标变量
        self.data_src_Val = self.data_src_box.GetStringSelection()

        # 保存按钮
        self.save_but = wx.Button(self.SysPanel, -1, "保存参数")
        self.save_but.Bind(wx.EVT_BUTTON, self._ev_save_para) # 绑定按钮事件

        vboxnetA = wx.BoxSizer(wx.VERTICAL)  # 纵向box
        vboxnetA.Add(sys_input_sizer, proportion=0, flag=wx.EXPAND | wx.BOTTOM, border=10)  # proportion参数控制容器尺寸比例
        vboxnetA.Add(self.data_store_box, proportion=0, flag=wx.EXPAND | wx.BOTTOM, border=10)
        vboxnetA.Add(self.data_src_box, proportion=0, flag=wx.EXPAND | wx.BOTTOM, border=10)
        vboxnetA.Add(self.save_but, proportion=0, flag=wx.ALIGN_CENTRE | wx.BOTTOM, border=10)

        self.SysPanel.SetSizer(vboxnetA)

        # 创建显示参数配置面板
        self.CtrlPanel = wx.Panel(self, -1)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=4, cols=4, vgap=10, hgap=10)

        # 界面参数配置
        self.sys_ind = {u'多子图MPL的单幅X大小': ["mpl_fig_x", 201],
                        u'多子图MPL的单幅Y大小': ["mpl_fig_y", 202],
                        u'多子图WEB的单幅X大小': ["web_size_x", 203],
                        u'多子图WEB的单幅Y大小': ["web_size_y", 204],
                        u'多子图MPL与左边框距离': ["mpl_fig_left", 205],
                        u'多子图MPL与右边框距离': ["mpl_fig_right", 206],
                        u'多子图MPL与上边框距离': ["mpl_fig_top", 207],
                        u'多子图MPL与下边框距离': ["mpl_fig_bottom", 208]}

        self.firm_mpl = {u'行情MPL与左边框距离': ["left", 301],
                         u'行情MPL与右边框距离': ["right", 302],
                         u'行情MPL与上边框距离': ["top", 303],
                         u'行情MPL与下边框距离': ["bottom", 304]}

        self.back_mpl = {u'回测MPL与左边框距离': ["left", 401],
                         u'回测MPL与右边框距离': ["right", 401],
                         u'回测MPL与上边框距离': ["top", 401],
                         u'回测MPL与下边框距离': ["bottom", 401]}

        for k, v in self.sys_ind.items():
            self.sys_ind_box = wx.StaticBox(self.CtrlPanel, -1, k)
            self.sys_ind_sizer = wx.StaticBoxSizer(self.sys_ind_box, wx.VERTICAL)
            self.sys_ind_input = wx.TextCtrl(self.CtrlPanel, v[1], str(self.sys_para["multi-panels"][v[0]]), style=wx.TE_PROCESS_ENTER)
            self.sys_ind_input.Bind(wx.EVT_TEXT_ENTER, self._ev_enter_stcode)
            self.sys_ind_sizer.Add(self.sys_ind_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
            # 加入Sizer中
            self.FlexGridSizer.Add(self.sys_ind_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)

        for k, v in self.firm_mpl.items():
            self.firm_mpl_box = wx.StaticBox(self.CtrlPanel, -1, k)
            self.firm_mpl_sizer = wx.StaticBoxSizer(self.firm_mpl_box, wx.VERTICAL)
            self.firm_mpl_input = wx.TextCtrl(self.CtrlPanel, v[1], str(self.firm_para["layout_dict"][v[0]]), style=wx.TE_PROCESS_ENTER)
            self.firm_mpl_input.Bind(wx.EVT_TEXT_ENTER, self._ev_enter_stcode)
            self.firm_mpl_sizer.Add(self.firm_mpl_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
            # 加入Sizer中
            self.FlexGridSizer.Add(self.firm_mpl_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)

        for k, v in self.back_mpl.items():
            self.back_mpl_box = wx.StaticBox(self.CtrlPanel, -1, k)
            self.back_mpl_sizer = wx.StaticBoxSizer(self.back_mpl_box, wx.VERTICAL)
            self.back_mpl_input = wx.TextCtrl(self.CtrlPanel, v[1], str(self.back_para["layout_dict"][v[0]]), style=wx.TE_PROCESS_ENTER)
            self.back_mpl_input.Bind(wx.EVT_TEXT_ENTER, self._ev_enter_stcode)
            self.back_mpl_sizer.Add(self.back_mpl_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
            # 加入Sizer中
            self.FlexGridSizer.Add(self.back_mpl_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)

        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        self.CtrlPanel.SetSizer(self.FlexGridSizer)

        self.HBoxPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.HBoxPanel.Add(self.SysPanel, proportion=2, border=2, flag=wx.EXPAND | wx.ALL)
        self.HBoxPanel.Add(self.CtrlPanel, proportion=10, border=2, flag=wx.EXPAND | wx.ALL)
        self.SetSizer(self.HBoxPanel)

    def _init_menu_bar(self):

        # 创建窗口面板
        menuBar = wx.MenuBar(style=wx.MB_DOCKABLE)

        toolmenu = wx.Menu()
        about = wx.MenuItem(toolmenu, wx.ID_ANY, '&使用帮助')
        toolmenu.Append(about)
        menuBar.Append(toolmenu, '&配置参数工具')

        mainmenu = wx.Menu()
        backitem = wx.MenuItem(mainmenu, wx.ID_ANY, '&返回')
        # 返回主菜单按钮
        self.Bind(wx.EVT_MENU, self._ev_switch_menu, backitem)  # 绑定事件
        mainmenu.Append(backitem)
        menuBar.Append(mainmenu, '&主菜单')

        self.SetMenuBar(menuBar)

    def _init_status_bar(self):

        self.statusBar = self.CreateStatusBar() # 创建状态条
        # 将状态栏分割为3个区域,比例为2:1
        self.statusBar.SetFieldsCount(3)
        self.statusBar.SetStatusWidths([-2, -1, -1])
        t = time.localtime(time.time())
        self.SetStatusText("公众号：元宵大师带你用Python量化交易", 0)
        self.SetStatusText("当前版本：%s" % Base_File_Oper.load_sys_para("sys_para.json")["__version__"], 1)
        self.SetStatusText(time.strftime("%Y-%B-%d %I:%M:%S", t), 2)

    def _ev_switch_menu(self, event):
        self.fun_swframe(0)  # 切换 Frame 主界面

    def _ev_save_para(self, event):

        self.sys_para["operate_sys"] = self.sel_operate_cmbo.GetStringSelection()
        Base_File_Oper.save_sys_para("sys_para.json", self.sys_para)
        MessageDialog("存储完成！点击界面顶部的菜单栏->主菜单->返回")

    def _ev_enter_stcode(self, event):

        if event.GetId() < 300:
            # 系统级显示
            for k, v in self.sys_ind.items():
               if v[1] == event.GetId():
                   self.sys_para["multi-panels"][v[0]] = int(event.GetString())
                   break
            Base_File_Oper.save_sys_para("sys_para.json", self.sys_para)

        elif event.GetId() < 400:
            # 行情MPL
            for k, v in self.firm_mpl.items():
               if v[1] == event.GetId():
                   self.firm_para["layout_dict"][v[0]] = float(event.GetString())
                   break
            Base_File_Oper.save_sys_para("firm_para.json", self.firm_para)

        else:
            # 回测MPL
            for k, v in self.back_mpl.items():
               if v[1] == event.GetId():
                   self.back_para["layout_dict"][v[0]] = float(event.GetString())
                   break
            Base_File_Oper.save_sys_para("back_para.json", self.back_para)
        MessageDialog("存储完成！")

class MainApp(wx.App):
    def OnInit(self):
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self.frame = ConfFrame()
        self.frame.Show()
        self.frame.Center()
        self.SetTopWindow(self.frame)
        return True

if __name__ == '__main__':
    app = MainApp()
    app.MainLoop()

