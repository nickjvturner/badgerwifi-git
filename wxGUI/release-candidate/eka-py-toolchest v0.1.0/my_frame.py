# my_frame.py

import wx
from drop_target import DropTarget
from validate_esx import validate
from unpack_esx import unpack
from rename_aps.rename_aps_IK import rename_aps
from summarise_esx import summarise
from generate_bom_xlsx import generate_bom
import os
from pathlib import Path


class MyFrame(wx.Frame):
    def __init__(self, parent, title):

        wx.Frame.__init__(self, parent, title=title, size=(700, 500))

        self.panel = wx.Panel(self)
        self.list_box = wx.ListBox(self.panel, style=wx.LB_EXTENDED)

        self.project_unpacked = False  # Initialize the state variable
        self.working_directory = ''
        self.project_name = ''

        self.config_dir = 'configuration'
        self.drop_target_contents = 'drop_target_contents.txt'
        self.config_path = Path.cwd() / self.config_dir / self.drop_target_contents
        self.load_drop_target_contents()  # Load file paths at startup

        self.display_log = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Set a monospaced font for display_log
        monospace_font = wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.display_log.SetFont(monospace_font)

        self.copy_log_button = wx.Button(self.panel, label="Copy Log")
        self.reset_button = wx.Button(self.panel, label="Reset")

        self.unpack_button = wx.Button(self.panel, label="Unpack .esx")
        self.rename_aps_button = wx.Button(self.panel, label="Rename APs")
        self.validate_button = wx.Button(self.panel, label="Validate")
        self.summarise_button = wx.Button(self.panel, label="Summarise")
        self.generate_bom_button = wx.Button(self.panel, label="Generate BoM")
        self.exit_button = wx.Button(self.panel, label="Exit")

        button_row1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_row1_sizer.Add(self.copy_log_button, 0, wx.ALL, 5)
        button_row1_sizer.AddStretchSpacer(1)
        button_row1_sizer.Add(self.unpack_button, 0, wx.ALL, 5)
        button_row1_sizer.Add(self.rename_aps_button, 0, wx.ALL, 5)

        button_row2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_row2_sizer.Add(self.reset_button, 0, wx.ALL, 5)
        button_row2_sizer.AddStretchSpacer(1)
        button_row2_sizer.Add(self.validate_button, 0, wx.ALL, 5)
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
        self.reset_button.Bind(wx.EVT_BUTTON, self.on_reset)

        self.unpack_button.Bind(wx.EVT_BUTTON, self.on_unpack)
        self.rename_aps_button.Bind(wx.EVT_BUTTON, self.on_rename_aps)
        self.validate_button.Bind(wx.EVT_BUTTON, self.on_validate)
        self.summarise_button.Bind(wx.EVT_BUTTON, self.on_summarise)
        self.generate_bom_button.Bind(wx.EVT_BUTTON, self.on_generate_bom)
        self.exit_button.Bind(wx.EVT_BUTTON, self.on_exit)

        self.list_box.Bind(wx.EVT_KEY_DOWN, self.on_delete_key)

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

    def save_drop_target_contents(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)  # Ensure the directory exists
        try:
            with open(self.config_path, 'w') as file:
                for filepath in self.list_box.GetStrings():
                    file.write(filepath + '\n')
        except Exception as e:
            wx.MessageBox(f"Error saving file paths: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def load_drop_target_contents(self):
        try:
            with open(self.config_path, 'r') as file:
                for line in file:
                    filepath = line.strip()
                    if filepath:  # Avoid adding empty lines
                        self.list_box.Append(filepath)
        except FileNotFoundError:
            # This exception is expected if the file doesn't exist yet (e.g., first run)
            pass
        except Exception as e:
            wx.MessageBox(f"Error loading file paths: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def on_reset(self, event):
        self.display_log.SetValue("")  # Clear the contents of the display_log
        self.project_unpacked = False  # Reset project_unpacked state

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
            # Create a message dialog with Yes and No buttons
            dlg = wx.MessageDialog(None, "Project has already been unpacked. Would you like to re-unpack it?",
                                   "Re-unpack project?", wx.YES_NO | wx.ICON_QUESTION)

            # Show the dialog and check the response
            result = dlg.ShowModal()

            if result == wx.ID_YES:
                # User wants to re-unpack the project
                self.project_unpacked = False
                self.unpack_project()
            else:
                # User chose not to re-unpack the project
                wx.MessageBox("Operation cancelled.", "Information", wx.OK | wx.ICON_INFORMATION)

            # Don't forget to destroy the dialog after using it
            dlg.Destroy()

    def on_validate(self, event):
        if not self.project_unpacked:
            self.unpack_project()
        self.validate_project()

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
        self.save_drop_target_contents()  # Save the file paths before exiting
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
            # self.unpack_button.Disable()
        pass

    def validate_project(self):
        validate(self.working_directory, self.project_name, self.append_message)

    def rename_aps(self):
        rename_aps(self.working_directory, self.project_name, self.append_message)

    def summarise_project(self):
        summarise(self.working_directory, self.project_name, self.append_message)

    def create_bom(self):
        generate_bom(self.working_directory, self.project_name, self.append_message)

    def save_file_paths(self):
        try:
            with open('file_paths.txt', 'w') as file:
                for filepath in self.list_box.GetStrings():
                    file.write(filepath + '\n')
        except Exception as e:
            wx.MessageBox(f"Error saving file paths: {e}", "Error", wx.OK | wx.ICON_ERROR)
