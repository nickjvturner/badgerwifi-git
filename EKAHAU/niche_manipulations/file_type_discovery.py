import magic


def identify_file_format(project_dir, message_callback):
    """Identify the file format of the files in the project directory."""
    message_callback(f"{nl}File formats in the project directory: {nl}")

    for file in project_dir.iterdir():
        if file.is_file():
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(file)
            message_callback(f'{file.name}: {file_type}')