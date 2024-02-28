# simple, y-axis.py

"""
Created with [SIMULATED APs] as the targets...

description
---
script unpacks Ekahau project file
loads accessPoints.json
places all APs into a list

sorts the list by:
    floor name
    x-axis value

the sorted list is iterated through and a new AP Name is assigned
AP numbering starts at 1, with:
    apSeqNum = 1
    this is an integer

AP Naming pattern is defined by:
    new_AP_name = f'AP-{apSeqNum:03}'
    this is an f-string
    {apSeqNum:03} is a formatted expression that represents the variable apSeqNum with specific formatting
    :03 specifies the formatting of this integer should be with leading zeros to have a width of 3 characters
    If apSeqNum is less than 100, it will be padded with leading zeros to ensure the resulting string has a total of 5 characters

Nick Turner
nickjvturner.com

@nickjvturner@mastodon.social

"""

import json
import shutil
from pathlib import Path


nl = '\n'

from common import load_json
from common import create_floor_plans_dict


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
                                                    i['location']['coord']['y']))

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
