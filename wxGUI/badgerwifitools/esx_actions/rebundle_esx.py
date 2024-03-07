# rebundle_esx.py

import shutil
from pathlib import Path
import threading

nl = '\n'


def rebundle_project(working_directory, project_name, message_callback):
    """Re-bundle the project directory into an .esx file."""

    new_file_base_name = project_name + '_re-zip'
    new_file_name_zip = new_file_base_name + '.zip'
    new_file_name_esx = new_file_base_name + '.esx'

    try:
        # Create a ZIP archive - shutil.make_archive adds the .zip extension automatically
        shutil.make_archive(new_file_base_name, 'zip', working_directory / project_name)
        shutil.move(new_file_name_zip, new_file_name_esx)

        message_callback(f'Process complete {new_file_name_esx} successfully re-bundled into .esx file')
    except Exception as e:
        print(e)


if __name__ == "__main__":
    rebundle_project(Path('/Users/nick/Desktop/esx_files'), 'test project', print)
    print('done')
