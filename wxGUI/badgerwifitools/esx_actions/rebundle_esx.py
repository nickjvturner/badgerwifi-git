# rebundle_esx.py

import wx
import shutil
from pathlib import Path

nl = '\n'


def rebundle_project(working_directory, project_name, message_callback):
    """Re-bundle the project directory into an .esx file."""

    project_dir = working_directory / project_name

    new_file_base_name = project_name + '_re-zip'
    new_file_name_zip = new_file_base_name + '.zip'
    new_file_name_esx = new_file_base_name + '.esx'

    try:
        # Create a ZIP archive - shutil.make_archive adds the .zip extension automatically
        shutil.make_archive(working_directory / new_file_base_name, 'zip', working_directory / project_name)
        shutil.move(working_directory / new_file_name_zip, working_directory / new_file_name_esx)

        wx.CallAfter(message_callback, f'{new_file_name_esx} successfully re-bundled into .esx file')
    except Exception as e:
        print(e)
        wx.CallAfter(message_callback, f"Error: Failed to re-bundle {project_name} into .esx file.")
