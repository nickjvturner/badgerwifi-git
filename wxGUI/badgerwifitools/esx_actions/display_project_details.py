from common import load_json
from common import create_floor_plans_dict


nl = '\n'

def display_project_details(working_directory, project_name, message_callback):
    """Display the project details."""

    project_dir = working_directory / project_name

    message_callback(f"Project name: {project_name}")
    message_callback(f"Project directory: {project_dir}{nl}")

    display_floor_plans_dict(project_dir, message_callback)


def display_floor_plans_dict(project_dir, message_callback):
    """Display the floor plans dictionary."""

    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    floor_plans_dict = create_floor_plans_dict(floor_plans_json)

    for floor_plan_id, floor_plan_name in floor_plans_dict.items():
        message_callback(f"{floor_plan_name}: {floor_plan_id}{nl}")
