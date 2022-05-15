#! /usr/bin/env python 
#-*- encoding: utf-8 -*- 
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx
import wx.adv
import wx.grid
import wx.html2
import os

class MainFrame(wx.Frame):

    rel_path = os.path.dirname(os.path.dirname(__file__)) + '/ConfigFiles/'

    def __init__(self, parent=None, id=-1, displaySize=(1600, 900), Fun_SwFrame=None):

        displaySize = 0.05 * displaySize[0], 0.35 * displaySize[1]

        wx.Frame.__init__(self, parent=None, title=u'', size=displaySize, style=wx.DEFAULT_FRAME_STYLE)

        self.fun_swframe = Fun_SwFrame
        toolbar = wx.ToolBar(self, style=wx.TB_VERTICAL)
        toolbar.AddTool(1100, '', wx.Bitmap(MainFrame.rel_path + "png/tab_quant.png"))
        toolbar.AddSeparator()
        toolbar.AddTool(1101, '', wx.Bitmap(MainFrame.rel_path + "png/tab_price.png"))
        toolbar.AddSeparator()
        toolbar.AddTool(1102, '', wx.Bitmap(MainFrame.rel_path + "png/tab_trade.png"))
        toolbar.AddSeparator()
        toolbar.AddTool(1103, '', wx.Bitmap(MainFrame.rel_path + "png/tab_config.png"))
        toolbar.Realize()
        toolbar.Bind(wx.EVT_TOOL, self.OnEventTrig)

    def OnEventTrig(self, event):
        if event.GetId() == 1100:  # 量化按钮
            self.fun_swframe(1)
        elif event.GetId() == 1101:  # 数据按钮
            self.fun_swframe(2)
        elif event.GetId() == 1102:  # 选股按钮
            self.fun_swframe(3)

        elif event.GetId() == 1103:  # 配置按钮
            self.fun_swframe(4)
        else:
            pass

