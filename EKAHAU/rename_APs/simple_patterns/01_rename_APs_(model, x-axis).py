#!/usr/bin/env python3

"""
Created with [SIMULATED APs] as the targets...

description
---
script unpacks Ekahau project file
loads accessPoints.json
places all APs into a list

sorts the list by:
    floor name
    model
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

import zipfile
import json
import shutil
import time
from pathlib import Path
from pprint import pprint


def main():
    nl = '\n'

    # Get filename and current working directory
    print(f'{nl}{Path(__file__).name}')
    print(f'working_directory: {Path.cwd()}{nl}')

    # Get local file with extension .esx
    for file in sorted(Path.cwd().iterdir()):
        # ignore files in directory containing _re-zip
        if (file.suffix == '.esx') and (not('re-zip' in file.stem)):
            proceed = input(f'Proceed with file: {str(file.name)}? (YES/no)')
            if proceed == 'no':
                exit()

            print('filename:', file.name)

            # Define the project name
            project_name = file.stem
            print('project_name:', project_name)

            # Unzip the .esx project file into folder named {project_name}
            with zipfile.ZipFile(file.name, 'r') as zip_ref:
                zip_ref.extractall(project_name)
            print('project successfully unzipped')

            # Load the floorPlans.json file into the floorPlansJSON Dictionary
            with open(Path(project_name) / 'floorPlans.json') as json_file:
                floorPlansJSON = json.load(json_file)
                json_file.close()
            # pprint(floorPlansJSON)

            # Create an intermediary dictionary to lookup floor names
            floorPlansDict = {}

            # Populate the intermediary dictionary
            for floor in floorPlansJSON['floorPlans']:
                floorPlansDict[floor['id']] = floor['name']
            # pprint(floorPlansDict)

            # Load the accessPoints.json file into the accessPointsJSON dictionary
            with open(Path(project_name) / 'accessPoints.json') as json_file:
                accessPointsJSON = json.load(json_file)
                json_file.close()
            # pprint(accessPointsJSON)

            # Convert accessPointsJSON from dictionary to list
            # We do this to make the sorting procedure more simple
            accessPointsLIST = []
            for ap in accessPointsJSON['accessPoints']:
                accessPointsLIST.append(ap)

            def floorPlanGetter(floorPlanId):
                # print(floorPlansDict.get(floorPlanId))
                return floorPlansDict.get(floorPlanId)

            # by floor name(floorPlanId lookup), tag:value(filtered within tagKeyGetter) and x coord
            accessPointsLIST_SORTED = sorted(accessPointsLIST,
                                             key=lambda i: (floorPlanGetter(i['location']['floorPlanId']),
                                                            i['model'],
                                                            i['location']['coord']['x']))

            apSeqNum = 1

            for ap in accessPointsLIST_SORTED:
                # Define new AP naming scheme
                # Define the pattern to rename your APs
                new_AP_name = f'AP-{apSeqNum:03}'

                print(f"[[ {ap['name']} [{ap['model']}]] from: {floorPlanGetter(ap['location']['floorPlanId'])} ] renamed to {new_AP_name}")

                ap['name'] = new_AP_name
                apSeqNum += 1
            # print(accessPointsLIST_SORTED)

            # Convert modified list back into dictionary
            sorted_accessPointsJSON_dict = {'accessPoints': accessPointsLIST_SORTED}
            # print(sorted_accessPointsJSON_dict)

            # save the modified dictionary as accessPoints.json
            with open("accessPoints.json", "w") as outfile:
                json.dump(sorted_accessPointsJSON_dict, outfile, indent=4)

            # move file into unpacked folder OVERWRITING ORIGINAL
            shutil.move('accessPoints.json', Path(project_name) / 'accessPoints.json')

            output_esx = Path(project_name + '_re-zip')

            try:
                shutil.make_archive(str(output_esx), 'zip', project_name)
                shutil.move(output_esx.with_suffix('.zip'), output_esx.with_suffix('.esx'))
                print(f'{nl}** Process complete **{nl}{output_esx} re-bundled into .esx file{nl}')
                shutil.rmtree(project_name)
                print(f'Temporary project contents directory removed{nl}')
            except Exception as e:
                print(e)


if __name__ == "__main__":
    start_time = time.time()
    main()
    run_time = time.time() - start_time
    print(f'** Time to run: {round(run_time, 2)} seconds **')
