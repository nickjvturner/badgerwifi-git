from common import load_json
from common import create_floor_plans_dict

import magic

nl = '\n'

def display_project_details(working_directory, project_name, message_callback):
    """Display the project details."""

    project_dir = working_directory / project_name

    message_callback(f"Project name: {project_name}")
    message_callback(f"Project directory: {project_dir}{nl}")

    display_floor_plans_dict(project_dir, message_callback)
    identify_file_format(project_dir, message_callback)


def display_floor_plans_dict(project_dir, message_callback):
    """Display the floor plans dictionary."""

    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    floor_plans_dict = create_floor_plans_dict(floor_plans_json)

    for floor_plan_id, floor_plan_name in floor_plans_dict.items():
        message_callback(f"{floor_plan_name}: {floor_plan_id}{nl}")

    # for floor_plan_id, floor_plan_name in floor_plans_dict.items():
    #     print(f"{floor_plan_id}: {floor_plan_name}")


def identify_file_format(project_dir, message_callback):
    """Identify the file format of the files in the project directory."""
    message_callback(f"{nl}File formats in the project directory: {nl}")

    for file in project_dir.iterdir():
        if file.is_file():
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(file)
            message_callback(f'{file.name}: {file_type}')



# def identify_file_format(file_path):
#     # Create a magic.Magic instance to detect the file type
#     mime = magic.Magic(mime=True)
#     file_type = mime.from_file(file_path)
#
#     return file_type
#
#
# # Example usage
# file_path = 'path/to/your/file'  # Make sure to provide the actual file path
# file_format = identify_file_format(file_path)
# print(f'The file format is: {file_format}')

