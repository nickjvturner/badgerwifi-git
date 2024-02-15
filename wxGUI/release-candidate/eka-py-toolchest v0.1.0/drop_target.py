# drop_target.py

import wx

class DropTarget(wx.FileDropTarget):
    def __init__(self, window, allowed_extensions, message_callback):
        wx.FileDropTarget.__init__(self)
        self.window = window
        self.allowed_extensions = allowed_extensions
        # New attribute to hold the callback function for appending messages
        self.message_callback = message_callback

    def OnDropFiles(self, x, y, filenames):
        # Track presence of .esx and .xlsx files separately
        esx_present = any(filepath.lower().endswith('.esx') for filepath in self.window.GetStrings())
        xlsx_present = any(filepath.lower().endswith('.xlsx') for filepath in self.window.GetStrings())

        for filepath in filenames:
            extension = filepath.lower().split('.')[-1]

            # Check if the file has "re-zip" in its name or is an unsupported extension
            if "re-zip" in filepath:
                self.message_callback(f"File {filepath} cannot be added because it contains 're-zip' in the name.")
                continue
            elif not any(filepath.lower().endswith(ext) for ext in self.allowed_extensions):
                self.message_callback(f"File {filepath} has an unsupported extension.")
                continue

            # Handling for .esx files
            if extension == 'esx':
                if esx_present or filepath in self.window.GetStrings():
                    self.message_callback(f"Only one .esx file can be added. {filepath} was not added.")
                    continue
                else:
                    self.window.Append(filepath)
                    esx_present = True  # Mark that an .esx file has been added

            # Handling for .xlsx files
            elif extension == 'xlsx':
                if xlsx_present or filepath in self.window.GetStrings():
                    self.message_callback(f"Only one .xlsx file can be added. {filepath} was not added.")
                    continue
                else:
                    self.window.Append(filepath)
                    xlsx_present = True  # Mark that an .xlsx file has been added

            # Handling for .docx files
            elif extension == 'docx':
                if filepath not in self.window.GetStrings():
                    self.window.Append(filepath)
                else:
                    self.message_callback(f"File {filepath} is already in the list.")

