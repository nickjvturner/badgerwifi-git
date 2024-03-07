# main.py

import wx
import sys
from pathlib import Path
from my_frame import MyFrame


def main():
    sys.path.append(str(Path(__file__).resolve().parent))
    app = wx.App()
    MyFrame(None, 'BadgerWiFi-tools')
    app.MainLoop()


if __name__ == '__main__':
    main()
