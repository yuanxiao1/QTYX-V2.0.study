#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx
import threading
import time


class ProgressBarDialog():

    def __init__(self, title="下载进度", message="剩余时间", total_len=0) :

        self.title = title
        self.message = message
        self.total_len = total_len

        self.dialog = wx.ProgressDialog(self.title, self.message, self.total_len,
                                        style=wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)


class ProgressBarThread(threading.Thread):
    """ 进度条类 """

    def __init__(self, parent, queue):
        """
        :param parent:  主线程UI
        :param timer:  计时器
        """
        super(ProgressBarThread, self).__init__()  # 继承
        self.parent = parent
        self.q_codes = queue
        self.setDaemon(True)  # 设置为守护线程， 即子线程是守护进程，主线程结束子线程也随之结束。

    def run(self):

        q_size = self.q_codes.qsize()  # 返回队列的大小

        while q_size != 0:
            q_size = self.q_codes.qsize()
            time.sleep(0.5)
            wx.CallAfter(self.parent.update_process_bar, q_size)  # 更新进度条进度
        wx.CallAfter(self.parent.close_process_bar)  # destroy进度条

