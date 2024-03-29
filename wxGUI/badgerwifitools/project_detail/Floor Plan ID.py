
from common import nl
from common import load_json
from common import create_floor_plans_dict


def run(working_directory, project_name, message_callback):
    """Display the project details."""

    project_dir = working_directory / project_name

    message_callback(f"Project name: {project_name}")
    message_callback(f"Project directory: {project_dir}{nl}")

    display_floor_plan_ids(project_dir, message_callback)


def display_floor_plan_ids(project_dir, message_callback):
    """Display the floor plan ids."""

    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    floor_plans_dict = create_floor_plans_dict(floor_plans_json)

    for floor_plan_id in floor_plans_dict:
        message_callback(f"{floor_plans_dict.get(floor_plan_id).get('name')}: {floor_plan_id}{nl}")