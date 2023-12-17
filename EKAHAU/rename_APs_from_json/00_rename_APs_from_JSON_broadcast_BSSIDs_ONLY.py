#!/usr/bin/env python3

"""
Put together by Nick Turner (nickjvturner.com)

script takes input json blob from Aruba Central, attempts to match
broadcast macaddrs with ekahau assigned AP Names

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

    # Get local file with extension .json
    for file in sorted(Path.cwd().iterdir()):
        # find and import JSON file:
        if file.suffix == '.json':
            proceed = input(f'Import JSON file: {str(file.name)}? (YES/no)')
            if proceed == 'no':
                exit()

            # Load the JSON file
            with open(file, 'r') as json_file:
                AP_name_to_BSSIDs = json.load(json_file)

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
                # Iterate through the dictionary items
                for key, mac_addresses in AP_name_to_BSSIDs.items():
                    # print(f"Key: {key}")

                    # Iterate through the MAC addresses within each item
                    for mac_address in mac_addresses:
                        # print(f"MAC Address: {mac_address}")

                        if ap['name'] == f"Measured AP-{mac_address[-5:]}":

                            new_AP_name = key

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
