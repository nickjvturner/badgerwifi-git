# my_frame.py

import wx
from drop_target import DropTarget
from inspect_esx import inspect
from unpack_esx import unpack
from rename_aps import rename_aps
from summarise_esx import summarise
from generate_bom_xlsx import generate_bom

class MyFrame(wx.Frame):
    def __init__(self, parent, title):

        wx.Frame.__init__(self, parent, title=title, size=(700, 500))

        self.panel = wx.Panel(self)
        self.list_box = wx.ListBox(self.panel, style=wx.LB_EXTENDED)

        # For testing purposes, automatically add the below file path to the ListBox
        self.list_box.Append("/Users/nick/Desktop/Odense.esx")

        self.project_unpacked = False  # Initialize the state variable
        self.working_directory = ''
        self.project_name = ''

        self.display_log = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Set a monospaced font for display_log
        monospace_font = wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.display_log.SetFont(monospace_font)

        self.copy_log_button = wx.Button(self.panel, label="Copy Log")
        self.clear_log_button = wx.Button(self.panel, label="Clear Log")

        self.unpack_button = wx.Button(self.panel, label="Unpack .esx")
        self.rename_aps_button = wx.Button(self.panel, label="Rename APs")
        self.inspect_button = wx.Button(self.panel, label="Inspect")
        self.summarise_button = wx.Button(self.panel, label="Summarise")
        self.generate_bom_button = wx.Button(self.panel, label="Generate BoM")
        self.exit_button = wx.Button(self.panel, label="Exit")

        button_row1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_row1_sizer.Add(self.copy_log_button, 0, wx.ALL, 5)
        button_row1_sizer.AddStretchSpacer(1)
        button_row1_sizer.Add(self.unpack_button, 0, wx.ALL, 5)
        button_row1_sizer.Add(self.rename_aps_button, 0, wx.ALL, 5)

        button_row2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_row2_sizer.Add(self.clear_log_button, 0, wx.ALL, 5)
        button_row2_sizer.AddStretchSpacer(1)
        button_row2_sizer.Add(self.inspect_button, 0, wx.ALL, 5)
        button_row2_sizer.Add(self.summarise_button, 0, wx.ALL, 5)
        button_row2_sizer.Add(self.generate_bom_button, 0, wx.ALL, 5)

        button_row3_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_row3_sizer.AddStretchSpacer(1)

        button_row4_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_row4_sizer.AddStretchSpacer(1)
        button_row4_sizer.Add(self.exit_button, 0, wx.ALL, 5)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.list_box, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.display_log, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(button_row1_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(button_row2_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(button_row3_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(button_row4_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.panel.SetSizer(main_sizer)

        self.create_menu()

        allowed_extensions = (".esx", ".docx", ".xlsx")  # Define allowed file extensions
        dt = DropTarget(self.list_box, allowed_extensions, self.append_message)
        self.list_box.SetDropTarget(dt)

        self.copy_log_button.Bind(wx.EVT_BUTTON, self.on_copy_log)
        self.clear_log_button.Bind(wx.EVT_BUTTON, self.on_clear_log)

        self.unpack_button.Bind(wx.EVT_BUTTON, self.on_unpack)
        self.rename_aps_button.Bind(wx.EVT_BUTTON, self.on_rename_aps)
        self.inspect_button.Bind(wx.EVT_BUTTON, self.on_inspect)
        self.summarise_button.Bind(wx.EVT_BUTTON, self.on_summarise)
        self.generate_bom_button.Bind(wx.EVT_BUTTON, self.on_generate_bom)
        self.exit_button.Bind(wx.EVT_BUTTON, self.on_exit)

        self.list_box.Bind(wx.EVT_KEY_DOWN, self.on_delete_key)

        # self.generate_bom_button.Disable()

        self.Center()
        self.Show()

    def create_menu(self):
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_ADD, "&Add File", "Add a file to the list")
        menubar.Append(file_menu, "&File")
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.on_add_file, id=wx.ID_ADD)

    def append_message(self, message):
        # Append a message to the message display area.
        self.display_log.AppendText(message + '\n')

    def on_clear_log(self, event):
        self.display_log.SetValue("")  # Clear the contents of the display_log

    def on_add_file(self, event):
        wildcard = "Ekahau Project file (*.esx)|*.esx"
        dlg = wx.FileDialog(self, "Choose a file", wildcard=wildcard,
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for path in paths:
                self.list_box.Append(path)
        dlg.Destroy()

    def on_delete_key(self, event):
        keycode = event.GetKeyCode()
        if keycode in [wx.WXK_DELETE, wx.WXK_BACK]:
            selected_indices = self.list_box.GetSelections()
            for index in reversed(selected_indices):
                self.list_box.Delete(index)

    def on_unpack(self, event):
        if not self.project_unpacked:
            self.unpack_project()
        else:
            wx.MessageBox("Project has already been unpacked.", "Information", wx.OK | wx.ICON_INFORMATION)

    def on_inspect(self, event):
        if not self.project_unpacked:
            self.unpack_project()
        self.inspect_project()

    def on_rename_aps(self, event):
        if not self.project_unpacked:
            self.unpack_project()
        self.rename_aps()

    def on_summarise(self, event):
        if not self.project_unpacked:
            self.unpack_project()
        self.summarise_project()

    def on_generate_bom(self, event):
        if not self.project_unpacked:
            self.unpack_project()
        self.create_bom()


    def on_copy_log(self, event):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.display_log.GetValue()))
            wx.TheClipboard.Close()
            self.append_message("Log copied to clipboard.")
        else:
            wx.MessageBox("Unable to access the clipboard.", "Error", wx.OK | wx.ICON_ERROR)


    def on_exit(self, event):
        self.Close()


    # Helper methods
    def get_specific_file_type(self, extension):
        for filepath in self.list_box.GetStrings():
            if filepath.lower().endswith(extension):
                return filepath
        self.append_message(f"No file with {extension} present in file list.")
        return None

    def unpack_project(self):
        if not self.project_unpacked:
            self.working_directory, self.project_name, self.project_unpacked = unpack(self.get_specific_file_type('.esx'), self.append_message)
            self.unpack_button.Disable()
        pass

    def inspect_project(self):
        inspect(self.working_directory, self.project_name, self.append_message)

    def rename_aps(self):
        rename_aps(self.working_directory, self.project_name, self.append_message)

    def summarise_project(self):
        summarise(self.working_directory, self.project_name, self.append_message)

    def create_bom(self):
        generate_bom(self.working_directory, self.project_name, self.append_message)
