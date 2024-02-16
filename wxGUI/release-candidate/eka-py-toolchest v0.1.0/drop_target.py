import wx

class DropTarget(wx.FileDropTarget):
    def __init__(self, window, allowed_extensions, message_callback):
        wx.FileDropTarget.__init__(self)
        self.window = window
        self.allowed_extensions = allowed_extensions
        # New attribute to hold the callback function for appending messages
        self.message_callback = message_callback

    def OnDropFiles(self, x, y, filenames):
        for filepath in filenames:
            if filepath.lower().endswith(self.allowed_extensions) and "re-zip" not in filepath:
                if filepath not in self.window.GetStrings():
                    self.window.Append(filepath)
                else:
                    self.message_callback(f"File {filepath} is already in the list.")
            elif "re-zip" in filepath:
                self.message_callback(f"File {filepath} cannot be added because it contains 're-zip' in the name.")
            else:
                self.message_callback(f"File {filepath} has an unsupported extension.")
        return True
