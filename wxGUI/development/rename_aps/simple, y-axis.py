# simple, y-axis.py

from pathlib import Path

from common import load_json
from common import create_floor_plans_dict

from common import save_and_move_json
from common import re_bundle_project

SHORT_DESCRIPTION = f"""Intended for simulated APs
Re-sorts APs by:
    floor name,
    y-axis value
    
AP-001, AP-002, AP-003..."""

LONG_DESCRIPTION = f"""Created with [SIMULATED APs] as the targets...

script loads accessPoints.json
places all APs into a list

sorts the list by:
    floor name
    y-axis value

the sorted list is iterated through and a new AP Name is assigned

AP Naming pattern is defined by:
    new_AP_name = f'AP-{{apSeqNum:03}}'
    
resulting AP names should look like:
    AP-001, AP-002, AP-003..."""

nl = '\n'


def run(working_directory, project_name, message_callback):
    message_callback(f'Performing action for: {project_name}')

    floor_plans_json = load_json(working_directory / project_name, 'floorPlans.json', message_callback)
    access_points_json = load_json(working_directory / project_name, 'accessPoints.json', message_callback)

    floor_plans_dict = create_floor_plans_dict(floor_plans_json)

    # Convert access_points_json from dictionary to list
    # We do this to make the sorting procedure more simple
    access_points_list = []
    for ap in access_points_json['accessPoints']:
        access_points_list.append(ap)

    # Sort the list of APs, by the floor name(floorPlanId lookup) and x coord
    access_points_list_sorted = sorted(access_points_list,
                                     key=lambda i: (floor_plans_dict.get(i['location']['floorPlanId'], ''),
                                                    i['location']['coord']['y']))

    ap_sequence_number = 1

    for ap in access_points_list_sorted:
        # Define new AP naming scheme
        # Define the pattern to rename your APs
        new_ap_name = f'AP-{ap_sequence_number:03}'

        message_callback(
            f"{ap['name']} {ap['model']} from: {floor_plans_dict.get(ap['location']['floorPlanId'])} renamed to {new_ap_name}")

        ap['name'] = new_ap_name
        ap_sequence_number += 1

    # Save and Move the Updated JSON
    updated_access_points_json = {'accessPoints': access_points_list_sorted}
    save_and_move_json(updated_access_points_json, working_directory / project_name / 'accessPoints.json')

    # Re-bundle into .esx File
    re_bundle_project(Path(working_directory / project_name), f"{project_name}_re-zip")
    message_callback(f"\nProcess complete\n{project_name}_re-zip re-bundled into .esx file")
