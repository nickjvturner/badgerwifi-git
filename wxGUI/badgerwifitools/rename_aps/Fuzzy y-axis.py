# Fuzzy y-axis.py

from pathlib import Path

from common import load_json
from common import create_floor_plans_dict
from common import create_floor_plans_height_dict

from common import save_and_move_json
from common import re_bundle_project

from common import model_sort_order
from common import rename_aps

nl = '\n'
VERTICAL_DIVISION_FACTOR = 40

SHORT_DESCRIPTION = f"""Intended for simulated APs

Sorts APs by:
    floor name,
    model,
    y-axis in 'bands',
    x-axis value

AP-001, AP-002, AP-003..."""

LONG_DESCRIPTION = f"""Created with [SIMULATED APs] as the targets...

script loads accessPoints.json
places all APs into a list

sorts the list by:
    floor name,
    model,
    y-axis in 'bands',
    x-axis value

the sorted list is iterated through and a new AP Name is assigned

AP Naming pattern is defined by:
    AP-{{apSeqNum:03}}
    
The resulting AP numbering looks like:
    AP-001, AP-002, AP-003...

per floor
script places all APs into a list
sorts the list by the y-axis value
iterates through the sorted list
the very first AP is assigned to y_coordinate_group 1
establish a value for the acceptable_deviation within the y-axis
    value is calculated by dividing the current map image height by the vertical_division_factor
    one twentieth of the current map image height
    I invite you to manually edit this value, if you so wish
subsequent APs with a y-axis value within the acceptable_deviation will also be assigned to y_coordinate_group 1
when an AP with a y-axis value greater than the acceptable_deviation is found, the y_coordinate_group id is incremented
the assessment of APs continues
eventually all APs are assigned a y_coordinate_group id
the list is re-sorted by:
    y_group, x-axis value
    specifically in this order
having been grouped into '20' (horizontal) rows
the APs are now sorted by their x-axis value within each row
the sorted list is iterated through and a new AP Name is assigned"""


def run(working_directory, project_name, message_callback):
    message_callback(f'Renaming APs within project: {project_name}')

    floor_plans_json = load_json(working_directory / project_name, 'floorPlans.json', message_callback)
    access_points_json = load_json(working_directory / project_name, 'accessPoints.json', message_callback)

    floor_plans_dict = create_floor_plans_dict(floor_plans_json)
    floor_plans_height_dict = create_floor_plans_height_dict(floor_plans_json)

    # Convert access_points_json from dictionary to list
    # We do this to make the sorting procedure more simple
    access_points_list = []
    for ap in access_points_json['accessPoints']:
        access_points_list.append(ap)

    # Sort the list of APs, by the floor name(floorPlanId lookup) and x coord
    access_points_list_sorted = sorted(access_points_list,
                                     key=lambda i: (floor_plans_dict.get(i['location']['floorPlanId'], ''),
                                                    i['location']['coord']['y']))

    y_coordinate_group = 1
    current_floor = 0
    current_y = None
    y_coordinate_threshold = None

    for ap in access_points_list_sorted:
        if current_floor != ap['location']['floorPlanId']:
            current_y = ap['location']['coord']['y']
            # Set a threshold for the maximum x-coordinate difference to be in the same group
            y_coordinate_threshold = int(
                floor_plans_height_dict.get(ap['location']['floorPlanId'])) / VERTICAL_DIVISION_FACTOR

        if abs(ap['location']['coord']['y'] - current_y) <= y_coordinate_threshold:
            ap['location']['coord']['y_group'] = y_coordinate_group
        else:
            y_coordinate_group += 1
            current_y = ap['location']['coord']['y']
            ap['location']['coord']['y_group'] = y_coordinate_group
        current_floor = ap['location']['floorPlanId']

    # by floor name(floorPlanId lookup) and x coord
    sorted_ap_list = sorted(access_points_list_sorted,
                                     key=lambda i: (floor_plans_dict.get(i['location']['floorPlanId'], ''),
                                                    model_sort_order.get(i['model'], i['model']),
                                                    i['location']['coord']['y_group'],
                                                    i['location']['coord']['x']))

    sorted_ap_list = rename_aps(sorted_ap_list, message_callback, floor_plans_dict)

    # Save and Move the Updated JSON
    updated_access_points_json = {'accessPoints': sorted_ap_list}
    save_and_move_json(updated_access_points_json, working_directory / project_name / 'accessPoints.json')

    # Re-bundle into .esx File
    re_bundle_project(Path(working_directory / project_name), f"{project_name}_re-zip")
    message_callback(f"\nProcess complete\n{project_name}_re-zip re-bundled into .esx file")
