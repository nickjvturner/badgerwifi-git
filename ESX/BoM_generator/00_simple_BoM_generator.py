#!/usr/bin/env python3

"""
Created by Nick Turner (@nickjvturner)

Super Ugly work in progress

Intended for Simulation project files

"""

import zipfile
import json
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

            ap_model_list = []

            for ap in accessPointsLIST:
                if ' +  ' in ap['model']:
                    # print('ap + ant detected')
                    # print((ap['model']).split(' +  ')[0])
                    ap_model_list.append((ap['model']).split(' +  ')[0])
                    ap_model_list.append((ap['model']).split(' +  ')[1])
                else:
                    ap_model_list.append(ap['model'])

            # print(ap_model)
            model_counter = {}

            for ap_model in ap_model_list:
                if ap_model not in model_counter:
                    model_counter[ap_model] = 0
                model_counter[ap_model] += 1

            # print(model_counter)
            print(f'{nl}{nl}')
            print(f'{file.stem}')
            for key, value in model_counter.items():
                print(f'{key} {value}')
            print(f'{nl}{nl}')

if __name__ == "__main__":
    start_time = time.time()
    main()
    run_time = time.time() - start_time
    print(f'** Time to run: {round(run_time, 2)} seconds **')
