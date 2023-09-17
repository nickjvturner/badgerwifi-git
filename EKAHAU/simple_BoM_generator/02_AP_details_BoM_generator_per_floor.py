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
from pathlib import Path
from collections import Counter
from pprint import pprint


def main():
    nl = '\n'

    def antennaIdentifier(ap):
        if 'model' in ap:
            if ' +  ' in ap['model']:
                apmodel_split_antenna = (ap['model']).split(' +  ')
                for entry in apmodel_split_antenna:
                    return ap_model_list

            elif ap['model'] == '':
                return 'measured AP, model unavailable, vendor: ' + ap['vendor']

            else:
                return ap['model']

        else:
            # print(ap)
            ap_model_list.append(f"measured AP, model & vendor information available")

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

            # Load the floorPlans.json file into the floorPlans Dictionary
            with open(Path(project_name) / 'floorPlans.json') as json_file:
                floorPlans = json.load(json_file)
                json_file.close()
            # pprint(floorPlans)

            # Create an intermediary dictionary to lookup floor names
            floorPlansDict = {}

            # Populate the intermediary dictionary
            for floor in floorPlans['floorPlans']:
                floorPlansDict[floor['id']] = floor['name']
            # pprint(floorPlansDict)

            # Load the accessPoints.json file into the accessPoints dictionary
            with open(Path(project_name) / 'accessPoints.json') as json_file:
                accessPoints = json.load(json_file)
                json_file.close()
            # pprint(accessPoints)

            # Load the simulatedRadios.json file into the simulatedRadios dictionary
            with open(Path(project_name) / 'simulatedRadios.json') as json_file:
                simulatedRadios = json.load(json_file)
            # pprint(simulatedRadios)

            # Create an intermediary dictionary to lookup simulated radio parameters
            simulatedRadioDict = {}

            # Populate the intermediary dictionary
            for radio in simulatedRadios['simulatedRadios']:
                simulatedRadioDict[radio['accessPointId']] = {}  # initialize nested dictionary
                for x, y in radio.items():
                    # print(x, y)
                    simulatedRadioDict[radio['accessPointId']][x] = y

            try:
            # Remove temporary directory containing unzipped project file
                shutil.rmtree(project_name)
            except Exception as e:
                print(e)

            print(f'{nl}{file.stem}')

            for floor in sorted(floorPlans['floorPlans'], key=lambda i: i['name']):

                accessPointsLIST = []

                print(floor['name'])
                print('-' * len(floor['name']))

                for ap in sorted(accessPoints['accessPoints'], key=lambda i: i['name']):
                    if not 'location' in ap:
                        # AP is not placed on any map
                        print('no map AP')
                        continue
                    elif ap['location']['floorPlanId'] == floor['id']:
                        accessPointsLIST.append(ap)

                        # model = antennaIdentifier(ap)

                        antennaTilt = simulatedRadioDict[ap['id']]['antennaTilt']
                        antennaMounting = simulatedRadioDict[ap['id']]['antennaMounting']
                        antennaHeight = simulatedRadioDict[ap['id']]['antennaHeight']

                        print(f"{ap['name']}, {ap['model']}, {antennaMounting}, {antennaHeight}, {antennaTilt}")

                print(f'{nl}')


if __name__ == "__main__":
    start_time = time.time()
    main()
    run_time = time.time() - start_time
    print(f'** Time to run: {round(run_time, 2)} seconds **')
