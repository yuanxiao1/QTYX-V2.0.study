#! /usr/bin/env python 
#-*- encoding: utf-8 -*- 
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx
import wx.adv
import wx.grid
import wx.html2
import wx.gizmos

class CollegeTreeListCtrl(wx.gizmos.TreeListCtrl):

    colleges = {
        u'经典策略': [
            {u'名称': u'N日突破', u'标识': u'趋势', '函数': u'已定义', 'define': "get_ndays_signal"},
            {u'名称': u'ATR止盈止损', u'标识': u'趋势', '函数': u'已定义', 'define': "get_ndays_atr_signal"}],
        u'自定义策略': [
            {u'名称': u'yx-zl-1', u'标识': u'综合', '函数': u'未定义'},
            {u'名称': u'yx-zl-2', u'标识': u'趋势', '函数': u'未定义'},
            {u'名称': u'yx-zl-3', u'标识': u'波动', '函数': u'未定义'}],
        u'衍生指标': [
            {u'名称': u'均线交叉', u'标识': u'cross', '函数': u'已定义'},
            {u'名称': u'跳空缺口', u'标识': u'jump', '函数': u'已定义'},
            {u'名称': u'黄金分割', u'标识': u'fibonacci', '函数': u'已定义'}],
        u'K线形态': [
            {u'名称': u'乌云盖顶', u'标识': u'CDLDARKCLOUDCOVER', '函数': u'已定义'},
            {u'名称': u'三只乌鸦', u'标识': u'CDL3BLACKCROWS', '函数': u'已定义'},
            {u'名称': u'十字星', u'标识': u'CDLDOJISTAR', '函数': u'已定义'},
            {u'名称': u'锤头', u'标识': u'CDLHAMMER', '函数': u'已定义'},
            {u'名称': u'射击之星', u'标识': u'CDLSHOOTINGSTAR', '函数': u'已定义'}
        ]
    }

    def __init__(self, parent=None, id=-1, pos=(0, 0), size=wx.DefaultSize,
                 style=wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT):

        wx.gizmos.TreeListCtrl.__init__(self, parent, id, pos, size, style)

        self.root = None
        self.InitUI()
        self.refDataShow(self.colleges)

    def InitUI(self):
        self.il = wx.ImageList(16, 16, True)
        self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (16, 16)))
        self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))
        self.SetImageList(self.il)
        self.AddColumn(u'名称')
        self.AddColumn(u'函数')
        self.SetColumnWidth(0, 150)
        self.SetColumnWidth(1, 100)

    def refDataShow(self, newDatas):
        # if self.root != None:
        #    self.DeleteAllItems()

        if newDatas != None:
            self.root = self.AddRoot(u'择时策略')
            self.SetItemText(self.root, "", 1) # 第1列上添加

            for cityID in newDatas.keys():# 填充整个树
                child = self.AppendItem(self.root, cityID)
                lastList = newDatas.get(cityID, [])
                self.SetItemText(child, cityID + u" (共" + str(len(lastList)) + u"个)", 0)
                self.SetItemImage(child, 0, which=wx.TreeItemIcon_Normal) # wx.TreeItemIcon_Expanded

                for index in range(len(lastList)):
                    college = lastList[index]  # TreeItemData是每一个ChildItem的唯一标示
                    # 以便在点击事件中获得点击项的位置信息
                    # "The TreeItemData class no longer exists, just pass your object directly to the tree instead
                    # data = wx.TreeItemData(cityID + "|" + str(index))
                    last = self.AppendItem(child, str(index), data=cityID + "|" + str(index))
                    self.SetItemText(last, college.get('名称', ''), 0)
                    self.SetItemText(last, str(college.get('函数', '')), 1)
                    self.SetItemImage(last, 0, which=wx.TreeItemIcon_Normal) # wx.TreeItemIcon_Expanded
                    self.Expand(self.root)


class CollegeTreeListCtrl1(wx.gizmos.TreeListCtrl):

    def __init__(self, parent=None, id=-1, pos=(0, 0), size=wx.DefaultSize,
                 style=wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT, tree_labels=[], tree_widths=[]):

        wx.gizmos.TreeListCtrl.__init__(self, parent, id, pos, size, style)

        self.root = None
        self.labels = tree_labels
        self.widths = tree_widths
        self.InitUI()

    def InitUI(self):
        self.il = wx.ImageList(16, 16, True)
        self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (16, 16)))
        self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))
        self.SetImageList(self.il)

        for num, label in enumerate(self.labels):
            self.AddColumn(label)
            self.SetColumnWidth(num, self.widths[num])

    def refDataShow(self, rootName, newDatas):

        if self.root != None:
            self.DeleteAllItems()

        if newDatas != None:

            for cityID in newDatas.keys():# 填充整个树

                if cityID == rootName:
                    # 创建根目录
                    self.root = self.AddRoot(rootName)
                    self.SetItemText(self.root, "", 1) # 第1列上添加

                    self.SetItemText(self.root, cityID + u"[" + str(len(newDatas[rootName])) + u"]", 0)
                    self.SetItemImage(self.root, 0, which=wx.TreeItemIcon_Normal) # wx.TreeItemIcon_Expanded

                    lastList = newDatas.get(cityID, [])

                    for index in range(len(lastList)):
                        college = lastList[index]  # TreeItemData是每一个ChildItem的唯一标示
                        # 以便在点击事件中获得点击项的位置信息
                        # "The TreeItemData class no longer exists, just pass your object directly to the tree instead
                        # data = wx.TreeItemData(cityID + "|" + str(index))
                        last = self.AppendItem(self.root, str(index), data=cityID + "|" + str(index))

                        for num, label in enumerate(self.labels):
                            self.SetItemText(last, str(college.get(self.labels[num], '')), num)

                        self.SetItemImage(last, 0, which=wx.TreeItemIcon_Normal)  # wx.TreeItemIcon_Expanded
                        self.Expand(self.root)

                """
                child = self.AppendItem(self.root, cityID)
                lastList = newDatas.get(cityID, [])
                self.SetItemText(child, cityID + u" (共" + str(len(lastList)) + u"个)", 0)
                self.SetItemImage(child, 0, which=wx.TreeItemIcon_Normal) # wx.TreeItemIcon_Expanded

                for index in range(len(lastList)):
                    college = lastList[index]  # TreeItemData是每一个ChildItem的唯一标示
                    # 以便在点击事件中获得点击项的位置信息
                    # "The TreeItemData class no longer exists, just pass your object directly to the tree instead
                    # data = wx.TreeItemData(cityID + "|" + str(index))
                    last = self.AppendItem(child, str(index), data=cityID + "|" + str(index))
                    self.SetItemText(last, college.get(self.labels[1], ''), 0)
                    self.SetItemText(last, str(college.get(self.labels[2], '')), 1)
                    self.SetItemImage(last, 0, which=wx.TreeItemIcon_Normal) # wx.TreeItemIcon_Expanded
                    self.Expand(self.root)
                """
    # 删除单个选项
    def DeleteSubjectItem(self, treeItemId):
        self.Delete(treeItemId)
        self.Refresh()

