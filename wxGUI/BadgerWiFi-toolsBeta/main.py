# main.py

import wx
import sys
from pathlib import Path
from my_frame import MyFrame


if __name__ == '__main__':
    sys.path.append(Path(__file__).resolve().parent)
    app = wx.App()
    MyFrame(None, 'BadgerWiFi-tools')
    app.MainLoop()