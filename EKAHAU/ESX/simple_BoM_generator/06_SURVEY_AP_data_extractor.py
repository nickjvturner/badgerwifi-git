#!/usr/bin/env python3

"""
Created by Nick Turner (@nickjvturner)

Super Ugly work in progress

Intended for Simulation project files

"""

import zipfile
import json
import time
import shutil
import openpyxl
from pathlib import Path
from pprint import pprint
import pandas as pd


def main():
    nl = '\n'

    # Get filename and current working directory
    print(f'{nl}{Path(__file__).name}')
    print(f'working_directory: {Path.cwd()}{nl}')

    # Get local file(s) with extension .esx
    for file in sorted(Path.cwd().iterdir()):
        # ignore files in directory containing _re-zip
        if (file.suffix == '.esx') and (not('re-zip' in file.stem)):
            proceed = input(f'Proceed with file: {str(file.name)}? (YES/no)')
            if proceed == 'no':
                continue

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

            # Create an intermediary dictionary to lookup floor names and populate it
            floorPlansDict = {
                floor['id']: floor['name'] for floor in floorPlansJSON['floorPlans']
            }

            pprint(floorPlansDict)

            # Load the accessPoints.json file into the accessPointsJSON dictionary
            with open(Path(project_name) / 'accessPoints.json') as json_file:
                accessPointsJSON = json.load(json_file)
                json_file.close()
            # pprint(accessPointsJSON)



            try:
                # Load the tagKey.json file into the notes dictionary
                with open(Path(project_name) / 'tagKeys.json') as json_file:
                    tagKeys = json.load(json_file)
                # pprint(tagKeys)

                # Create an intermediary dictionary to lookup simulated radio parameters
                tagKeyDict = {}

                # Populate the intermediary dictionary
                for tagKey in tagKeys['tagKeys']:
                    # print(tagKey)
                    tagKeyDict[tagKey['id']] = {}  # initialize nested dictionary
                    for x, y in tagKey.items():
                        # print(x, y)
                        tagKeyDict[tagKey['id']][x] = y
            except Exception as e:
                print(f'tagKeys.json not found inside project file, this probably means that there are no APs with tags')

            # pprint(tagKeyDict)

            try:
                # Remove temporary directory containing unzipped project file
                shutil.rmtree(project_name)
            except Exception as e:
                print(e)

            processedAPdict = {}

            for ap in accessPointsJSON['accessPoints']:
                    processedAPdict[ap['name']] = {
                        'name': ap['name'],
                        'vendor': ap.get('vendor', ''),
                        'model': ap.get('model', ''),
                        'floor': floorPlansDict.get(ap.get('location', {}).get('floorPlanId', ''), '')
                    }

                    for tag in ap['tags']:
                        if tag['tagKeyId'] in tagKeyDict:
                                processedAPdict[ap['name']][tagKeyDict[tag['tagKeyId']]['key']] = tag['value']


            pprint(processedAPdict)

            # Create a pandas dataframe from the data
            df = pd.DataFrame(processedAPdict)

            # Transpose the dataframe so that the keys become columns and the values become rows
            df = df.transpose()

            # Sort the dataframe by the 'floor' and 'model' columns in ascending order
            df = df.sort_values(by=['floor', 'name'], ascending=True)

            # Export the dataframe to an excel file
            df.to_excel(f'{file.stem}.xlsx', index=False)


if __name__ == "__main__":
    start_time = time.time()
    main()
    run_time = time.time() - start_time
    print(f'** Time to run: {round(run_time, 2)} seconds **')
