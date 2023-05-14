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
import pandas as pd
from pathlib import Path
import xlsxwriter
from collections import Counter
from pprint import pprint


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

            # Load the floorPlans.json file into the floorPlans Dictionary
            with open(Path(project_name) / 'floorPlans.json') as json_file:
                floorPlans = json.load(json_file)
                json_file.close()
            # pprint(floorPlans)

            # Create an intermediary dictionary to lookup floor names
            # populate it
            floorPlansDict = {
                floor['id']: floor['name'] for floor in floorPlans['floorPlans']
            }
            # pprint(floorPlansDict)

            # Create a simple list of floorPlans
            floorPlansList = []

            for floor, name in floorPlansDict.items():
                floorPlansList.append(name)
            # print(floorPlansList)

            # Load the accessPoints.json file into the accessPoints dictionary
            with open(Path(project_name) / 'accessPoints.json') as json_file:
                accessPoints = json.load(json_file)
                json_file.close()
            # pprint(accessPoints)

            # Load the simulatedRadios.json file into the simulatedRadios dictionary
            with open(Path(project_name) / 'simulatedRadios.json') as json_file:
                simulatedRadios = json.load(json_file)
            # pprint(simulatedRadios)

            # Create an intermediary dictionary to lookup simulated radio parameters and populate it
            # using dictionary comprehension
            simulatedRadioDict = {radio['accessPointId']: {x: y for x, y in radio.items()}
                                  for radio in simulatedRadios['simulatedRadios']}

            # pprint(simulatedRadioDict)

            processedAPdict = {}

            for ap in accessPoints['accessPoints']:
                processedAPdict[ap['name']] = {
                    'name': ap['name'],
                    'vendor': ap.get('vendor', ''),
                    'model': ap.get('model', ''),
                    'floor': floorPlansDict.get(ap.get('location', {}).get('floorPlanId', ''), ''),
                    'antennaTilt': simulatedRadioDict.get(ap['id'], {}).get('antennaTilt', ''),
                    'antennaMounting': simulatedRadioDict.get(ap['id'], {}).get('antennaMounting', ''),
                    'antennaHeight': simulatedRadioDict.get(ap['id'], {}).get('antennaHeight', '')
                }

            # pprint(processedAPdict)

            try:
            # Remove temporary directory containing unzipped project file
                shutil.rmtree(project_name)
            except Exception as e:
                print(e)

            print(f'{nl}{file.stem}')

            version = '1.2'
            output_filename = f'{file.stem} - BoM v{version}.xlsx'
            writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')

            for floor in sorted(floorPlansList):

                floorAPs = {}

                print(floor)
                print('-' * len(floor))

                for ap, ap_details in processedAPdict.items():
                    if ap_details['floor'] == floor:
                        floorAPs.update({ap: processedAPdict[ap]})

                # Create a pandas dataframe from the data
                df = pd.DataFrame(floorAPs)

                # Transpose the dataframe so that the keys become columns and the values become rows
                df = df.transpose()

                # Sort the dataframe by the 'floor' and 'model' columns in ascending order
                df = df.sort_values(by=['name'], ascending=True)

                # Export the dataframe to an excel file
                df.to_excel(writer, sheet_name=floor, index=False)

            # Create a pandas dataframe from the data
            df = pd.DataFrame(processedAPdict)

            # Transpose the dataframe so that the keys become columns and the values become rows
            df = df.transpose()

            # Sort the dataframe by the 'floor' and 'model' columns in ascending order
            df = df.sort_values(by=['floor', 'name'], ascending=True)

            # Export the dataframe to an excel file
            df.to_excel(writer, sheet_name='ALL APs', index=False)

            # Close the ExcelWriter object
            writer.close()

if __name__ == "__main__":
    start_time = time.time()
    main()
    run_time = time.time() - start_time
    print(f'** Time to run: {round(run_time, 2)} seconds **')
