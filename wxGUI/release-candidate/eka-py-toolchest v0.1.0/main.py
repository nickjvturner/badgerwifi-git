# main.py

import wx
import sys
from pathlib import Path
from my_frame import MyFrame


if __name__ == '__main__':
    sys.path.append(str(Path.cwd()))
    app = wx.App()
    MyFrame(None, 'eka-py-toolchest')
    app.MainLoop()