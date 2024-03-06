from common import load_json
from common import create_floor_plans_dict


def display_floor_plans_dict(working_directory, project_name, message_callback):
    """Display the floor plans dictionary."""

    project_dir = working_directory / project_name

    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    floor_plans_dict = create_floor_plans_dict(floor_plans_json)

    for floor_plan_id, floor_plan_name in floor_plans_dict.items():
        message_callback(f"{floor_plan_name}: {floor_plan_id}")

    # for floor_plan_id, floor_plan_name in floor_plans_dict.items():
    #     print(f"{floor_plan_id}: {floor_plan_name}")

