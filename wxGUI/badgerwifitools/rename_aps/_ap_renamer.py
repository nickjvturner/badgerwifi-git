# simple, x-axis.py

from pathlib import Path

from common import load_json
from common import create_floor_plans_dict

from common import save_and_move_json
from common import re_bundle_project
from common import rename_aps

from common import rename_process_completion_message as completion_message


def ap_renamer(working_directory, project_name, script_module, message_callback, boundary_separation=None):
    message_callback(f'Renaming APs within project: {project_name}')

    floor_plans_json = load_json(working_directory / project_name, 'floorPlans.json', message_callback)
    access_points_json = load_json(working_directory / project_name, 'accessPoints.json', message_callback)

    floor_plans_dict = create_floor_plans_dict(floor_plans_json)

    # Convert access_points_json from dictionary to list
    # We do this to make the sorting procedure more simple
    access_points_list = []
    for ap in access_points_json['accessPoints']:
        access_points_list.append(ap)

    if hasattr(script_module, 'SAR'):
        script_module.run(working_directory, project_name, message_callback)

    else:
        # Sort the list of APs, by the floor name(floorPlanId lookup) and x coord
        if hasattr(script_module, 'dynamic_widget'):
            access_points_list_sorted = script_module.sort_logic(access_points_list, floor_plans_dict, boundary_separation)

        else:
            access_points_list_sorted = script_module.sort_logic(access_points_list, floor_plans_dict)

        access_points_list_renamed = rename_aps(access_points_list_sorted, message_callback, floor_plans_dict)

        # Save and Move the Updated JSON
        updated_access_points_json = {'accessPoints': access_points_list_renamed}
        save_and_move_json(updated_access_points_json, working_directory / project_name / 'accessPoints.json')

        # Re-bundle into .esx File
        re_bundle_project(Path(working_directory / project_name), f"{project_name}_re-zip")
        completion_message(message_callback, project_name)
