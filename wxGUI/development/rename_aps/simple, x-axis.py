# simple, x-axis.py

from pathlib import Path

from common import load_json
from common import create_floor_plans_dict

from common import save_and_move_json
from common import re_bundle_project

# CONSTANTS

SHORT_DESCRIPTION = f"""Intended for simulated APs
Re-sorts APs by:
    floor name,
    x-axis value"""

LONG_DESCRIPTION = f"""Created with Simulated APs as the intended targets

loads accessPoints.json
places APs into a list

sorts the list by:
    floor name
    x-axis value

the sorted list is iterated through and a new AP Name is assigned

AP numbering starts at 1, with:
    apSeqNum = 1

AP Naming pattern is defined by:
    new_AP_name = f'AP-{{apSeqNum:03}}'

resulting AP names should look like:
    AP-001, AP-002, AP-003..."""

nl = '\n'


def run(working_directory, project_name, message_callback):
    message_callback(f'Performing action for: {project_name}')

    floorPlansJSON = load_json(working_directory / project_name, 'floorPlans.json', message_callback)
    accessPointsJSON = load_json(working_directory / project_name, 'accessPoints.json', message_callback)

    floorPlansDict = create_floor_plans_dict(floorPlansJSON)

    # Convert accessPointsJSON from dictionary to list
    # We do this to make the sorting procedure more simple
    accessPointsList = []
    for ap in accessPointsJSON['accessPoints']:
        accessPointsList.append(ap)

    # Sort the list of APs, by the floor name(floorPlanId lookup) and x coord
    accessPointsListSorted = sorted(accessPointsList,
                                     key=lambda i: (floorPlansDict.get(i['location']['floorPlanId'], ''),
                                                    i['location']['coord']['x']))

    apSeqNum = 1

    for ap in accessPointsListSorted:
        # Define new AP naming scheme
        # Define the pattern to rename your APs
        new_AP_name = f'AP-{apSeqNum:03}'

        message_callback(
            f"{ap['name']} {ap['model']} from: {floorPlansDict.get(ap['location']['floorPlanId'])} renamed to {new_AP_name}")

        ap['name'] = new_AP_name
        apSeqNum += 1

    # Save and Move the Updated JSON
    updatedAccessPointsJSON = {'accessPoints': accessPointsListSorted}
    save_and_move_json(updatedAccessPointsJSON, working_directory / project_name / 'accessPoints.json')

    # Re-bundle into .esx File
    re_bundle_project(Path(working_directory / project_name), f"{project_name}_re-zip")
    message_callback(f"\nProcess complete\n{project_name}_re-zip re-bundled into .esx file")
