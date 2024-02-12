#!/usr/bin/env python3

"""
Created with [SIMULATED APs] as the targets...

description
---
script unpacks Ekahau project file
loads accessPoints.json
places all APs into a list

sorts the list by:
    custom tag value 1
    custom tag value 2
    floor name
    custom tag value 3
    x-axis value

the sorted list is iterated through and a new AP Name is assigned
AP numbering starts at 1, with:
    apSeqNum = 1
    this is an integer

AP Naming pattern is defined by:
    new_AP_name = f"{sortTagValueGetter(ap['tags'])}-AP{apSeqNum:03}"
    includes custom tag value in the AP name

Nick Turner
nickjvturner.com

@nickjvturner@mastodon.social

"""

import zipfile
import json
import shutil
import time
from pathlib import Path


def main():
    nl = '\n'

    # Get current working directory
    print(f'{nl}{Path(__file__).name}')
    print(f'working_directory: {Path.cwd()}{nl}')

    # Get local file with extension .esx
    for file in sorted(Path.cwd().iterdir()):
        # ignore files in directory containing _re-zip
        if (file.suffix == '.esx') and (not ('re-zip' in file.stem)):
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

            # Try to load the tagKeys.json file into the tagKeysJSON dictionary
            try:
                with open(Path(project_name) / 'tagKeys.json') as json_file:
                    tagKeysJSON = json.load(json_file)
                    json_file.close()
                # pprint(tagKeysJSON)

                # Create an intermediary dictionary to lookup tags
                tagKeysDict = {}

                # Populate the intermediary dictionary
                for tag in tagKeysJSON['tagKeys']:
                    tagKeysDict[tag['key']] = tag['id']

            except Exception as e:
                print(e)
                pass

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

            def sortTagValueGetter(tagsList, sortTagKey):
                # function receives a list containing a dictionary of unique tag ids and corresponding values
                undefined_TagValue = '-   ***   TagValue is empty   ***   -'

                # If sortTagKey is missing, substitute with:
                # 'A' - group and number APs without tags before APs with tags
                # 'Z' - group and number APs without tags after APs with tags
                missing_TagKey = 'Z'

                # Safely get the unique Id that corresponds with this key
                sortTagUniqueId = tagKeysDict.get(sortTagKey)
                if sortTagUniqueId is None:
                    return missing_TagKey

                for value in tagsList:
                    if value.get('tagKeyId') == sortTagUniqueId:
                        tagValue = value.get('value')
                        if tagValue is None:
                            return undefined_TagValue
                        return tagValue
                return missing_TagKey


            # Use .sorted and lambda functions to sort the list in order
            # by floor name(floorPlanId lookup)
            # specified tag:value(filtered within sortTagValueGetter function)
            # x coordinate (this numbers the APs from left to right)
            accessPointsLIST_SORTED = sorted(accessPointsLIST,
                                             key=lambda i: (
                                                 sortTagValueGetter(i.get('tags', []), 'UNIT'),
                                                 sortTagValueGetter(i.get('tags', []), 'building-group'),
                                                 floorPlanGetter(i['location'].get('floorPlanId', 'missing_floorPlanId')),
                                                 sortTagValueGetter(i.get('tags', []), 'sequence-override'),
                                                 i['location']['coord']['x']
                                             ))

            apSeqNum = 1

            for ap in accessPointsLIST_SORTED:
                # Define new AP naming pattern
                new_AP_name = f"{sortTagValueGetter(ap['tags'], 'UNIT')}-AP{apSeqNum:03}"

                print(
                    f"[[ {ap['name']} [{ap['model']} ]] from map: {floorPlanGetter(ap['location']['floorPlanId'])} | sorting tag: {sortTagValueGetter(ap['tags'], 'UNIT')} ] renamed to {new_AP_name}")

                ap['name'] = new_AP_name
                apSeqNum += 1
            # print(accessPointsLIST_SORTED)

            # Convert modified list back into dictionary
            sorted_accessPointsJSON_dict = {'accessPoints': accessPointsLIST_SORTED}
            # print(sorted_accessPointsJSON_dict)

            print('re-bundling modified files back into .esx file... Please wait')

            # save the modified dictionary as accessPoints.json
            with open("accessPoints.json", "w") as outfile:
                json.dump(sorted_accessPointsJSON_dict, outfile, indent=4)

            # move modified accessPoints.json into unpacked folder OVERWRITING ORIGINAL
            shutil.move('accessPoints.json', Path(project_name) / 'accessPoints.json')

            output_stem = str(Path(file.stem + '_re-zip'))

            output_zip = output_stem + '.zip'
            output_esx = output_stem + '.esx'

            try:
                shutil.make_archive(output_stem, 'zip', project_name)
                shutil.move(output_zip, output_esx)
                print(f'{nl}Process complete {output_esx} re-bundled{nl}')

                shutil.rmtree(project_name)
                print(f"Temp folder used to unzip project file, REMOVED, you're welcome")
            except Exception as e:
                print(e)


if __name__ == "__main__":
    start_time = time.time()
    main()
    run_time = time.time() - start_time
    print(f'** Time to run: {round(run_time, 2)} seconds **')
