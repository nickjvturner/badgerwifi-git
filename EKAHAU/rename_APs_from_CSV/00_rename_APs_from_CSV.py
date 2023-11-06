#!/usr/bin/env python3

"""
Created by Nick Turner (@nickjvturner)

This script is created with [SIMULATED APs] as the targets...
Script will rename all APs throughout each floor from left to right

"""

import csv
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

    # Get local file with extension .csv
    for file in sorted(Path.cwd().iterdir()):
        # find and import CSV file with required column headers:
        # AP name, Ekahau AP Name
        if file.suffix == '.csv':
            proceed = input(f'Import CSV file: {str(file.name)}? (YES/no)')
            if proceed == 'no':
                exit()

            # Create a dictionary to store AP Name to Ekahau AP Name mapping
            AP_names_dict = {}

            try:
                # Open and read the CSV file using DictReader
                with open(file, 'r', newline='') as CSVfile:
                    reader = csv.DictReader(CSVfile)

                    # Access and process the data using column header names
                    for row in reader:
                        AP_names_dict[row['Ekahau AP Name']] = row['AP Name']

            except FileNotFoundError:
                print(f"File not found: {csv_file_path}")

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

            for ap in accessPointsLIST:
                if ap['name'] in AP_names_dict:
                    new_AP_name = AP_names_dict[ap['name']]

                    print(f"{ap['name']} becomes {new_AP_name}")

                    ap['name'] = new_AP_name

            # Convert modified list back into dictionary
            modified_accessPointsJSON_dict = {'accessPoints': accessPointsLIST}
            # print(sorted_accessPointsJSON_dict)

            # save the modified dictionary as accessPoints.json
            with open("accessPoints.json", "w") as outfile:
                json.dump(modified_accessPointsJSON_dict, outfile, indent=4)

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
