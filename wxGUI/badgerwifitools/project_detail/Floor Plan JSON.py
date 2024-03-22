# Floor Plan JSON.py

from common import nl
from common import load_json
from PIL import Image


def create_custom_floor_plans_dict(floor_plans_json):
    """Create a dictionary of floor plans."""
    floor_plans_dict = {}
    for floor in floor_plans_json['floorPlans']:
        floor_plans_dict[floor['name']] = floor
    return floor_plans_dict


def run(working_directory, project_name, message_callback):
    """Display the project details."""

    project_dir = working_directory / project_name

    message_callback(f"Project name: {project_name}")
    message_callback(f"Project directory: {project_dir}{nl}")

    display_floor_plans_dict(project_dir, message_callback)


def display_floor_plans_dict(project_dir, message_callback):
    """Display the floor plans dictionary."""

    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    custom_floor_plans_dict = create_custom_floor_plans_dict(floor_plans_json)

    for floor_plan_name, floor_plan_data in sorted(custom_floor_plans_dict.items()):
        message_callback(f"{nl}{floor_plan_name}:{nl}")

        for key in floor_plan_data:
            message_callback(f"{key}: {floor_plan_data[key]}")
