#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx

class ClassifySelectDiag(wx.Dialog):

    def __init__(self, parent, title, map_table):
        super(wx.Dialog, self).__init__(parent, title=title+"分类选择"+"(左边未选/右边已选)",
                                        size=(350, 500), style=wx.DEFAULT_FRAME_STYLE)

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.HORIZONTAL)

        self.map_table = map_table
        self.unselect = wx.ListBox(panel, choices=list(self.map_table["未选择"].keys()), style=wx.LB_SINGLE)
        self.select = wx.ListBox(panel, choices=list(self.map_table["已选择"].keys()), style=wx.LB_SINGLE)

        box.Add(self.unselect, 1, wx.EXPAND)
        box.Add(self.select, 1, wx.EXPAND)

        panel.SetSizer(box)
        panel.Fit()

        self.Centre()
        self.Bind(wx.EVT_LISTBOX, self.onUnSelListBox, self.unselect)
        self.Bind(wx.EVT_LISTBOX, self.onSelListBox, self.select)
        self.Show(True)

    def onUnSelListBox(self, event):

        nameSelected = event.GetEventObject().GetStringSelection()
        indexSelected = event.GetEventObject().GetSelections()

        self.map_table["已选择"].update({nameSelected: self.map_table["未选择"][nameSelected]})
        self.map_table["未选择"].pop(nameSelected)

        self.unselect.Delete(indexSelected[0])
        self.select.InsertItems([nameSelected], 0)


    def onSelListBox(self, event):

        nameSelected = event.GetEventObject().GetStringSelection()
        indexSelected = event.GetEventObject().GetSelections()

        self.map_table["未选择"].update({nameSelected:self.map_table["已选择"][nameSelected]})
        self.map_table["已选择"].pop(nameSelected)
        self.select.Delete(indexSelected[0])
        self.unselect.InsertItems([nameSelected], 0)

    def feedback_map(self):

        return self.map_table