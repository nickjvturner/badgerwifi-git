# unpack_esx.py

import zipfile

nl = '\n'


def unpack_esx_file(working_directory, project_name, esx_filepath, message_callback):
    """
    Unpacks the specified .esx file into a directory.
    """

    try:
        # Unzip the .esx project file into a folder named after the project_name
        message_callback(f'Unpacking .esx project: {project_name}')
        with zipfile.ZipFile(esx_filepath, 'r') as zip_ref:
            zip_ref.extractall(working_directory / project_name)
        message_callback(f"Project successfully unzipped{nl}")
        return True
    except Exception as e:
        message_callback('Failed to unpack project file: ' + str(e))
        return False
