# backup_esx.py

import shutil
from pathlib import Path
from datetime import datetime


def backup_esx(working_directory, esx_project_name, esx_filepath, message_callback):
    """
    Create a backup of .esx file in a new directory date and time stamped
    """

    # Create a backup folder if it doesn't exist
    backup_folder = working_directory / f"{esx_project_name}_BACKUP"
    backup_folder.mkdir(parents=True, exist_ok=True)

    # Generate a unique name for the backup .esx file with timestamp
    current_time = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    backup_esx_filename = Path(f"{esx_filepath.stem}_backup_{current_time}.esx").name
    backup_esx_path = backup_folder / backup_esx_filename

    try:
        # Copy the original .esx file to the backup folder
        shutil.copy2(esx_filepath, backup_esx_path)
        message_callback(f"{esx_project_name}.esx file backed up to '{backup_esx_path}'.")
    except Exception as e:
        message_callback(f"Error backing up .esx file: {e}")
