import wx
import os

from common import nl


def pretty_format_directory_structure(structure, level=0):
    formatted_structure = ""
    for directory, sub_dirs in structure.items():
        formatted_structure += "    " * level + "├── " + directory + "\n"
        if sub_dirs:
            formatted_structure += pretty_format_directory_structure(sub_dirs, level + 1)
    return formatted_structure


def create_directory_structure(root_dir, structure):
    for directory, sub_dirs in structure.items():
        dir_path = os.path.join(root_dir, directory)
        os.makedirs(dir_path, exist_ok=True)

        if sub_dirs:
            create_directory_structure(dir_path, sub_dirs)


def preview_directory_structure(self):
    pretty_directory_structure = pretty_format_directory_structure(self.current_dir_structure_profile.directory_structure)
    self.append_message(f"Preview of selected Directory Structure Profile:{nl}{nl}{pretty_directory_structure}")


def select_root_and_create_directory_structure(self):
    # Open a directory dialog to select a directory
    dlg = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
        root_directory = dlg.GetPath()
        self.append_message(f"Selected directory:{nl}{root_directory}{nl}{nl}Creating directory structure...")

        create_directory_structure(root_directory, self.current_dir_structure_profile.directory_structure)

        pretty_directory_structure = pretty_format_directory_structure(self.current_dir_structure_profile.directory_structure)
        self.append_message(f"{nl}{pretty_directory_structure}{nl}{nl}Directory structure created successfully.")

    dlg.Destroy()
