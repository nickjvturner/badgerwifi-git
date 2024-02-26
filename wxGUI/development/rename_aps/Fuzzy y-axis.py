# Fuzzy y-axis.py

from pathlib import Path

from common import load_json
from common import create_floor_plans_dict
from common import create_floor_plans_height_dict

# from common import rename_access_points
from common import save_and_move_json
from common import re_bundle_project

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
the sorted list is iterated through and a new AP Name is assigned
AP numbering starts at 1, with:
    apSeqNum = 1
    this is an integer
AP Naming pattern is defined by:
    new_AP_name = f'AP-{{apSeqNum:03}}'
    this is an f-string
    {{apSeqNum:03}} is a formatted expression that represents the variable apSeqNum with specific formatting
    :03 specifies the formatting of this integer should be with leading zeros to have a width of 3 characters
    If apSeqNum is less than 100, it will be padded with leading zeros to ensure the resulting string has a total of 5 characters
"""



def run(working_directory, project_name, message_callback):
    message_callback(f'Performing action for: {project_name}')

    floorPlansJSON = load_json(working_directory / project_name, 'floorPlans.json')
    accessPointsJSON = load_json(working_directory / project_name, 'accessPoints.json')

    floorPlansDict = create_floor_plans_dict(floorPlansJSON)
    floorPlansHeightDict = create_floor_plans_height_dict(floorPlansJSON)

    # Convert accessPointsJSON from dictionary to list
    # We do this to make the sorting procedure more simple
    accessPointsList = []
    for ap in accessPointsJSON['accessPoints']:
        accessPointsList.append(ap)

    # Sort the list of APs, by the floor name(floorPlanId lookup) and x coord
    accessPointsListSorted = sorted(accessPointsList,
                                     key=lambda i: (floorPlansDict.get(i['location']['floorPlanId'], ''),
                                                    i['location']['coord']['y']))

    y_coordinate_group = 1
    current_floor = 0
    current_y = None
    y_coordinate_threshold = None


    for ap in accessPointsListSorted:
        if current_floor != ap['location']['floorPlanId']:
            current_y = ap['location']['coord']['y']
            # Set a threshold for the maximum x-coordinate difference to be in the same group
            y_coordinate_threshold = int(
                floorPlansHeightDict.get(ap['location']['floorPlanId'])) / VERTICAL_DIVISION_FACTOR

        if abs(ap['location']['coord']['y'] - current_y) <= y_coordinate_threshold:
            ap['location']['coord']['y_group'] = y_coordinate_group
        else:
            y_coordinate_group += 1
            current_y = ap['location']['coord']['y']
            ap['location']['coord']['y_group'] = y_coordinate_group
        current_floor = ap['location']['floorPlanId']

    # by floor name(floorPlanId lookup) and x coord
    accessPointsListSorted = sorted(accessPointsListSorted,
                                     key=lambda i: (floorPlansDict.get(i['location']['floorPlanId'], ''),
                                                    i['model'],
                                                    i['location']['coord']['y_group'],
                                                    i['location']['coord']['x']))

    # Start numbering APs from... 1
    apSeqNum = 1

    for ap in accessPointsListSorted:
        # Define new AP naming scheme
        # Define the pattern to rename your APs
        new_AP_name = f'AP-{apSeqNum:03}'

        message_callback(
            f"[[ {ap['name']} [{ap['model']}]] from: {floorPlansDict.get(ap['location']['floorPlanId'])} ] renamed to {new_AP_name}")

        ap['name'] = new_AP_name
        apSeqNum += 1

    # Save and Move the Updated JSON
    updatedAccessPointsJSON = {'accessPoints': accessPointsListSorted}
    save_and_move_json(updatedAccessPointsJSON, working_directory / project_name / 'accessPoints.json')

    # Re-bundle into .esx File
    re_bundle_project(Path(working_directory / project_name), f"{project_name}_re-zip")
    message_callback(f"\nProcess complete\n{project_name}_re-zip re-bundled into .esx file")

