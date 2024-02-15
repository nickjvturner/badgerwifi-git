#!/usr/bin/env python3

"""
This script takes 2x inputs:
+ output.json
+ ekahau project file

output.json is a filtered dump from Aruba Central
List BSSIDs

base_url = 'https://apigw-eucentral3.central.arubanetworks.com'
request_endpoint = '/monitoring/v2/bssids'
group_filter = 'the group within Aruba Central'
limit = 300  # Must be larger than the total number of APs within the intended group

request_url = f'{base_url}{request_endpoint}?group={group_filter}&limit={str(limit)}'

The output from Aruba Central should be processed into a dictionary containing only:
+ AP Name
+ base radio macaddrs  # 2 or 3 depending on the number of radios present

The script will:
 + unzip the ekahau project file
 + load the accessPoints.json file into a dictionary
 + iterate through the APs
 + calculate all 16 possible BSSIDs from the base radio macaddrs
 + compare the last 5x characters of the ekahau assigned AP name with the possible BSSIDs
 + when a match is found replace the ekahau assigned AP name with the actual hostname pulled from Aruba Central

This script considers the last 2x characters of the macaddrs
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
            pprint(accessPointsJSON)

            # Convert accessPointsJSON from dictionary to list
            # We do this to make the sorting procedure more simple
            accessPointsLIST = []
            for ap in accessPointsJSON['accessPoints']:
                accessPointsLIST.append(ap)

            for ap in accessPointsLIST:
                print(ap['name'])
                # Iterate through the dictionary items
                for key, mac_addresses in AP_name_to_BSSIDs.items():
                    # print(f"Key: {key}")

                    # Iterate through the MAC addresses within each item
                    for mac_address in mac_addresses:
                        # print(f"MAC Address: {mac_address}")

                        penultimate_octet_str = mac_address[-5:-3]

                        final_octet_hex_str = mac_address[-2:]
                        final_octet_int = int(final_octet_hex_str, 16)

                        for i in range(16):
                            ekahau_assigned_AP_name = f"Measured AP-{penultimate_octet_str}:{final_octet_hex_str}"
                            # print(ekahau_assigned_AP_name)
                            if ap['name'] == ekahau_assigned_AP_name:

                                new_AP_name = key
                                print(f"{ap['name']} becomes {new_AP_name}")

                                ap['name'] = new_AP_name

                            final_octet_int += 1
                            final_octet_hex = hex(final_octet_int)[2:]  # Remove '0x' prefix

                            # padding the resulting hex was necessary to capture base macs that ended '00'
                            final_octet_hex_str = f"{final_octet_hex:0>2}"

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
