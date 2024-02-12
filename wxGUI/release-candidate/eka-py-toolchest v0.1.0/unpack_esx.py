from pathlib import Path
import zipfile

nl = '\n'

def unpack(file_path, message_callback):
    """
    Unpacks the specified .esx file into a directory.

    Parameters:
    - file_path: The path to the .esx file to be unpacked.
    - message_callback: A callback function for logging messages.
    """
    file = Path(file_path)
    message_callback('Unpacking File: ' + file.name)
    project_name = file.stem
    message_callback('Project name: ' + project_name)
    working_directory = file.parent
    message_callback('Working directory: ' + str(working_directory))

    try:
        # Unzip the .esx project file into a folder named after the project_name
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(working_directory / project_name)
        message_callback(f"Project successfully unzipped{nl}")
        return True
    except Exception as e:
        message_callback('Failed to unpack project file: ' + str(e))
        return False
