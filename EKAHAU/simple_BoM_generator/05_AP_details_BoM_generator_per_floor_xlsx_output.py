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
import openpyxl
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

            def externalAntSplitAnt(model_string):
                if ' +  ' in model_string:
                    apmodel_split_antenna = model_string.split(' +  ')
                    return apmodel_split_antenna[1]
                else:
                    return 'integrated'

            def externalAntSplitModel(model_string):
                if ' +  ' in model_string:
                    apmodel_split_antenna = model_string.split(' +  ')
                    return apmodel_split_antenna[0]
                else:
                    return model_string


            processedAPdict = {}

            for ap in accessPoints['accessPoints']:
                processedAPdict[ap['name']] = {
                    'name': ap['name'],
                    'vendor': ap.get('vendor', ''),
                    'model': externalAntSplitModel(ap.get('model', '')),
                    'antenna': externalAntSplitAnt(ap.get('model', '')),
                    'floor': floorPlansDict.get(ap.get('location', {}).get('floorPlanId', ''), ''),
                    'antennaTilt': simulatedRadioDict.get(ap['id'], {}).get('antennaTilt', ''),
                    'antennaMounting': simulatedRadioDict.get(ap['id'], {}).get('antennaMounting', ''),
                    'antennaHeight': simulatedRadioDict.get(ap['id'], {}).get('antennaHeight', ''),
                    'remarks': '',
                    'ap bracket': '',
                    'antenna bracket': ''
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

            # Create an empty dataframe
            df = pd.DataFrame()

            # Export the dataframe to an excel file
            df.to_excel(writer, sheet_name='TOTALS', index=False)

            ap_models_per_floor_to_be_totalled = {}
            antennas_per_floor_to_be_totalled = {}

            for floor in sorted(floorPlansList):

                floorAPs = {}
                floorAPmodels = set()
                floorAntennaTypes = set()

                print(floor)
                print('-' * len(floor))

                for ap, ap_details in processedAPdict.items():
                    if ap_details['floor'] == floor:
                        floorAPs.update({ap: processedAPdict[ap]})
                        floorAPmodels.add(ap_details['model'])
                        floorAntennaTypes.add(ap_details['antenna'])

                # print(floorAPmodels)


                # Create a pandas dataframe from the data
                df = pd.DataFrame(floorAPs)

                # Transpose the dataframe so that the keys become columns and the values become rows
                df = df.transpose()

                # Sort the dataframe by the 'floor' and 'model' columns in ascending order
                df = df.sort_values(by=['name'], ascending=True)

                # Export the dataframe to an excel file
                df.to_excel(writer, sheet_name=floor, index=False)

                ws = writer.sheets[floor]

                populated_columns = []

                for col in df.columns:
                    col_idx = df.columns.get_loc(col)
                    col_letter = openpyxl.utils.get_column_letter(col_idx + 1)
                    ws.set_column(f"{col_letter}:{col_letter}", 15)
                    populated_columns.append(col_letter)

                last_letter = populated_columns[-1]

                totals_key_column = chr(ord(last_letter) + 2)
                totals_value_column = chr(ord(last_letter) + 3)
                ws.set_column(f"{totals_key_column}:{totals_key_column}", 15)
                ws.set_column(f"{totals_value_column}:{totals_value_column}", 15)



                for index, ap_model in enumerate(floorAPmodels):
                    index += 2
                    ws.write(f'{totals_key_column}{index}', ap_model)
                    ws.write(f'{totals_value_column}{index}', f'=COUNTIF(C:C, {totals_key_column}{index})')

                    # Check if key exists, if not create it with default value
                    if ap_model not in ap_models_per_floor_to_be_totalled:
                        # print(ap_model)
                        ap_models_per_floor_to_be_totalled.update({ap_model: []})
                    ap_models_per_floor_to_be_totalled[ap_model].append(f"'{floor}'!{totals_value_column}{index}")


                for index, antenna in enumerate(floorAntennaTypes):
                    index += 4 + len(floorAPmodels)
                    ws.write(f'{totals_key_column}{index}', antenna)
                    ws.write(f'{totals_value_column}{index}', f'=COUNTIF(D:D, {totals_key_column}{index})')

                    # Check if key exists, if not create it with default value
                    if antenna not in antennas_per_floor_to_be_totalled:
                        antennas_per_floor_to_be_totalled.update({antenna: []})
                    antennas_per_floor_to_be_totalled[antenna].append(f"'{floor}'!{totals_value_column}{index}")

            # print(ap_models_per_floor_to_be_totalled)
            # print(antennas_per_floor_to_be_totalled)

            # Create a pandas dataframe from the data
            df = pd.DataFrame(processedAPdict)

            # Transpose the dataframe so that the keys become columns and the values become rows
            df = df.transpose()

            # Sort the dataframe by the 'floor' and 'model' columns in ascending order
            df = df.sort_values(by=['floor', 'name'], ascending=True)

            # Export the dataframe to an excel file
            df.to_excel(writer, sheet_name='ALL APs', index=False)


            ws = writer.sheets['TOTALS']

            for index, (key, value) in enumerate(ap_models_per_floor_to_be_totalled.items()):
                index += 1
                print(index, key, value)

                formula = f"=SUM({', '.join(value)})"

                ws.write(f'A{index}', key)
                ws.write(f'B{index}', formula)


            for index, (key, value) in enumerate(antennas_per_floor_to_be_totalled.items()):
                index += 3 + len(floorAPmodels)
                print(index, key, value)

                formula = f"=SUM({', '.join(value)})"

                ws.write(f'A{index}', key)
                ws.write(f'B{index}', formula)

            ws.set_column('A:A', 15)
            ws.set_column('B:B', 10)


            # Close the ExcelWriter object
            writer.close()

if __name__ == "__main__":
    start_time = time.time()
    main()
    run_time = time.time() - start_time
    print(f'** Time to run: {round(run_time, 2)} seconds **')
