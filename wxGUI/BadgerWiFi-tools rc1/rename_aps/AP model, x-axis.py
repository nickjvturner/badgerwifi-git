# simple, x-axis.py

import json
import shutil
from pathlib import Path

from common import load_json
from common import create_floor_plans_dict

# CONSTANTS

SHORT_DESCRIPTION = f"""Intended for simulated APs

Sorts APs by:
    floor name,
    model,
    x-axis value

AP-001, AP-002, AP-003..."""

LONG_DESCRIPTION = f"""Created with [SIMULATED APs] as the targets...

script loads accessPoints.json
places all APs into a list

sorts the list by:
    floor name,
    model,
    x-axis value

the sorted list is iterated through and a new AP Name is assigned

AP numbering starts at 1, with:
    apSeqNum = 1  # this is an integer

AP Naming pattern is defined by:
    new_AP_name = f'AP-{{apSeqNum:03}}'  # this is an f-string
    
    {{apSeqNum:03}}
    #is a formatted expression that represents the variable apSeqNum with specific formatting
    :03 specifies the formatting of this integer should be displayed with leading zeros to have a width of 3 characters
    If apSeqNum is less than 100, it will be padded with leading zeros to ensure the resulting string has a total of 3 characters
"""

nl = '\n'


def run(working_directory, project_name, message_callback):
    message_callback(f'Performing action for: {project_name}')

    floorPlansJSON = load_json(working_directory / project_name, 'floorPlans.json')
    accessPointsJSON = load_json(working_directory / project_name, 'accessPoints.json')

    floorPlansDict = create_floor_plans_dict(floorPlansJSON)

    # Convert accessPointsJSON from dictionary to list
    # We do this to make the sorting procedure more simple
    accessPointsList = []
    for ap in accessPointsJSON['accessPoints']:
        accessPointsList.append(ap)

    # Sort the list of APs, by the floor name(floorPlanId lookup) and x coord
    accessPointsListSorted = sorted(accessPointsList,
                                     key=lambda i: (floorPlansDict.get(i['location']['floorPlanId'], ''),
                                                    i['model'],
                                                    i['location']['coord']['x']))

    apSeqNum = 1

    for ap in accessPointsListSorted:
        # Define new AP naming scheme
        # Define the pattern to rename your APs
        new_AP_name = f'AP-{apSeqNum:03}'

        message_callback(f"[[ {ap['name']} [{ap['model']}]] from: {floorPlansDict.get(ap['location']['floorPlanId'])} ] renamed to {new_AP_name}")

        ap['name'] = new_AP_name
        apSeqNum += 1

    # Convert modified list back into dictionary
    accessPointsSortedDict = {'accessPoints': accessPointsListSorted}

    # save the modified dictionary as accessPoints.json
    with open("accessPoints.json", "w") as outfile:
        json.dump(accessPointsSortedDict, outfile, indent=4)

    # move file into unpacked folder OVERWRITING ORIGINAL
    shutil.move('accessPoints.json', working_directory / project_name / 'accessPoints.json')

    output_esx = Path(project_name + '_re-zip')

    try:
        shutil.make_archive(str(output_esx), 'zip', project_name)
        shutil.move(output_esx.with_suffix('.zip'), output_esx.with_suffix('.esx'))
        message_callback(f'{nl}** Process complete **{nl}{output_esx} re-bundled into .esx file{nl}')
        shutil.rmtree(project_name)
        message_callback(f'Temporary project contents directory removed{nl}')
    except Exception as e:
        print(e)
