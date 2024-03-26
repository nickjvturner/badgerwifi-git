# drop_target.py

import wx
from pathlib import Path


class DropTarget(wx.FileDropTarget):
    def __init__(self, window, allowed_extensions, message_callback, esx_project_unpacked, update_esx_project_unpacked_callback, drop_target_label_callback):
        super(DropTarget, self).__init__()
        self.window = window
        self.allowed_extensions = allowed_extensions
        self.ignored_extensions = ('.DS_Store')
        self.message_callback = message_callback
        self.esx_project_unpacked = esx_project_unpacked
        self.update_esx_project_unpacked_callback = update_esx_project_unpacked_callback
        self.drop_target_label_callback = drop_target_label_callback

    def OnDragOver(self, x, y, d):
        # This method can be used to provide feedback while moving over the target
        return wx.DragCopy

    def OnDropFiles(self, x, y, filenames):

        def process_file(filepath):
            existing_files = self.window.GetStrings()  # Get currently listed files

            if "re-zip" in filepath:
                self.message_callback(
                    f"{Path(filepath).name} cannot be added because it contains 're-zip' in the name.")
                return

            if filepath.endswith(self.ignored_extensions):
                return

            if not filepath.lower().endswith(self.allowed_extensions):
                self.message_callback(f"{Path(filepath).name} has an unsupported extension.")
                return

            if filepath in existing_files:
                self.message_callback(f"{Path(filepath).name} is already in the list.")
                return

            if filepath.lower().endswith('.esx'):
                # Initialize a flag to track if the .esx file is replaced or added
                existing_esx_in_list = False

                # Check if there is an existing .esx file in the list
                for index, existing_file in enumerate(existing_files):
                    if existing_file.lower().endswith('.esx'):
                        # There is already an .esx file in the list, show replace dialog
                        existing_esx_in_list = True  # Mark the file as processed
                        if not Path(existing_file).exists():
                            self.window.Delete(index)  # Remove the existing .esx file
                            self.window.Append(filepath)  # Append the new one
                            self.message_callback(f'{existing_file} replaced with {filepath}')
                            self.esx_project_unpacked = False
                            self.update_esx_project_unpacked_callback(False)

                        elif self.show_replace_dialog(filepath):
                            self.message_callback(f"{Path(self.window.GetStrings()[0]).name} removed.")
                            self.window.Delete(index)  # Remove the existing .esx file
                            self.window.Append(filepath)  # Append the new one
                            self.message_callback(f"{Path(filepath).name} added to the list.")
                            self.esx_project_unpacked = False
                            self.update_esx_project_unpacked_callback(False)
                        break  # Exit the loop after dealing with the first .esx file found

                # If no existing .esx file was found or replacement was not approved, append the new file
                if not existing_esx_in_list:
                    self.window.Append(filepath)
                    self.message_callback(f"{Path(filepath).name} added to the list.")

            if filepath.lower().endswith('.docx'):
                self.window.Append(filepath)
                self.message_callback(f"{Path(filepath).name} added to the list.")

            if self.window.GetCount() > 0:
                self.drop_target_label_callback(hide=True)

        for dropped_item in filenames:
            dropped_path = Path(dropped_item)
            if dropped_path.is_dir():
                # Recursively process all files in the dropped directory
                for file in dropped_path.rglob('*'):
                    process_file(str(file))
            else:
                process_file(dropped_item)

        return True

    def show_replace_dialog(self, filepath):
        # Dialog asking if the user wants to replace the existing .esx file
        dlg = wx.MessageDialog(self.window,
                               f"A .esx file is already present. Do you want to replace it with {Path(filepath).name}?",
                               "Replace File?", wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        return result
