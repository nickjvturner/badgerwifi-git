# main.py

import wx
from my_frame import MyFrame

if __name__ == '__main__':
    app = wx.App()
    MyFrame(None, 'eka-py-toolchest')
    app.MainLoop()
