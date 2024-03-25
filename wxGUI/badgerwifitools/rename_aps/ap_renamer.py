# simple, x-axis.py

from pathlib import Path

from common import load_json
from common import create_floor_plans_dict

from common import save_and_move_json
from common import re_bundle_project
from common import rename_aps

from common import rename_process_completion_message as completion_message
from common import BOUNDARY_SEPARATION_WIDGET
from common import RENAMED_APS_PROJECT_APPENDIX


def ap_renamer(working_directory, project_name, script_module, message_callback, boundary_separation=None):
    message_callback(f'Renaming APs within project: {project_name}')

    floor_plans_json = load_json(working_directory / project_name, 'floorPlans.json', message_callback)
    access_points_json = load_json(working_directory / project_name, 'accessPoints.json', message_callback)

    floor_plans_dict = create_floor_plans_dict(floor_plans_json)

    project_dir = Path(working_directory) / project_name

    # Create directory to hold output directories
    output_dir = working_directory / 'OUTPUT'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory for Blank floor plans
    renamed_aps_project_dir = output_dir / 'RENAMED APs'
    renamed_aps_project_dir.mkdir(parents=True, exist_ok=True)

    # Convert access_points_json from dictionary to list
    # We do this to make the sorting procedure more simple
    access_points_list = []
    for ap in access_points_json['accessPoints']:
        access_points_list.append(ap)

    if hasattr(script_module, 'SAR'):
        script_module.run(working_directory, project_name, message_callback)

    else:
        # Sort the list of APs, by the floor name(floorPlanId lookup) and x coord
        if hasattr(script_module, BOUNDARY_SEPARATION_WIDGET):
            access_points_list_sorted = script_module.sort_logic(access_points_list, floor_plans_dict, boundary_separation)

        else:
            access_points_list_sorted = script_module.sort_logic(access_points_list, floor_plans_dict)

        access_points_list_renamed = rename_aps(access_points_list_sorted, message_callback, floor_plans_dict)

        # Save and Move the Updated JSON
        updated_access_points_json = {'accessPoints': access_points_list_renamed}
        save_and_move_json(updated_access_points_json, working_directory / project_name / 'accessPoints.json')

        output_project_name = f"{project_name}{RENAMED_APS_PROJECT_APPENDIX}"

        # Re-bundle into .esx File
        re_bundle_project(project_dir, renamed_aps_project_dir, output_project_name)
        completion_message(message_callback, output_project_name)
