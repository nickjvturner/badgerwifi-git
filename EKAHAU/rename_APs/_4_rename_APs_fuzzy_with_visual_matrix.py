#!/usr/bin/env python3

"""
Created by Nick Turner (@nickjvturner)

This script is created with [SIMULATED APs] as the targets...
Script will rename all APs throughout each floor from left to right

"""

import zipfile
import json
import shutil
import time
import cv2
from pathlib import Path
from pprint import pprint


def main():
    nl = '\n'

    x_division_factor = 40
    y_division_factor = 10

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
                floorPlansDict[floor['id']] = {'name': floor['name'],
                                               'width': floor['width'],
                                               'height': floor['height'],
                                               'imageId': floor['imageId']
                                               }

            # print(floorPlansDict)

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
                return floorPlansDict[floorPlanId]['name']


            # by floor name(floorPlanId lookup) and x coord
            accessPointsLIST_SORTED = sorted(accessPointsLIST,
                                             key=lambda i: (floorPlanGetter(i['location']['floorPlanId']),
                                                            i['location']['coord']['x']))




            x_coordinate_group = 1
            current_floor = 0

            for ap in accessPointsLIST_SORTED:
                if current_floor != ap['location']['floorPlanId']:
                    current_x = ap['location']['coord']['x']
                    # Set a threshold for the maximum x-coordinate difference to be in the same group
                    x_coordinate_threshold = int(floorPlansDict[ap['location']['floorPlanId']]['width'])/x_division_factor

                if abs(ap['location']['coord']['x'] - current_x) <= x_coordinate_threshold:
                    ap['location']['coord']['x_group'] = x_coordinate_group
                else:
                    x_coordinate_group += 1
                    current_x = ap['location']['coord']['x']
                    ap['location']['coord']['x_group'] = x_coordinate_group
                current_floor = ap['location']['floorPlanId']


            # by floor name(floorPlanId lookup) and y coord
            accessPointsLIST_SORTED = sorted(accessPointsLIST,
                                             key=lambda i: (floorPlanGetter(i['location']['floorPlanId']),
                                                            i['location']['coord']['y']))

            y_coordinate_group = 1
            current_floor = 0

            for ap in accessPointsLIST_SORTED:
                if current_floor != ap['location']['floorPlanId']:
                    current_y = ap['location']['coord']['y']
                    # Set a threshold for the maximum x-coordinate difference to be in the same group
                    y_coordinate_threshold = int(floorPlansDict[ap['location']['floorPlanId']]['width']) / y_division_factor

                if abs(ap['location']['coord']['y'] - current_y) <= y_coordinate_threshold:
                    ap['location']['coord']['y_group'] = y_coordinate_group
                else:
                    y_coordinate_group += 1
                    current_y = ap['location']['coord']['y']
                    ap['location']['coord']['y_group'] = y_coordinate_group
                current_floor = ap['location']['floorPlanId']


            # by floor name(floorPlanId lookup) and x coord
            accessPointsLIST_SORTED = sorted(accessPointsLIST,
                                             key=lambda i: (floorPlanGetter(i['location']['floorPlanId']),
                                                            i['model'],
                                                            i['location']['coord']['y_group'],
                                                            i['location']['coord']['x_group']))



            for key in floorPlansDict.keys():
                # Join strings inside a Path object
                image_path = Path(project_name) / f"image-{floorPlansDict[key]['imageId']}"

                # Convert Path object to string
                image_path_str = str(image_path)

                # Load an image from file
                img = cv2.imread(image_path_str)

                # Check if the image is successfully loaded
                if img is not None:
                    height, width, _ = img.shape
                    y_interval = height // y_division_factor
                    x_interval = width // x_division_factor

                    lines_image = img.copy()

                    for i in range(1, y_division_factor + 1):
                        y = i * y_interval
                        cv2.line(lines_image, (0, y), (width, y), (0, 0, 0), 4)

                    for i in range(1, x_division_factor + 1):
                        x = i * x_interval
                        cv2.line(lines_image, (x, 0), (x, height), (0, 0, 0), 4)


                    # Display the image in a window
                    cv2.imshow(floorPlansDict[key]['name'], lines_image)

                    # Wait for a key event and close the window when a key is pressed


                    # Press 'any key' to continue
                    if cv2.waitKey(0) == ord('q'):
                        cv2.destroyAllWindows()
                        break

                    elif cv2.waitKey(0):
                        cv2.destroyAllWindows()

                else:
                    print('Image not loaded. Check the file path.')





            apSeqNum = 1

            for ap in accessPointsLIST_SORTED:
                # Define new AP naming scheme
                # Define the pattern to rename your APs
                new_AP_name = f'AP-{apSeqNum:03}'

                print(
                    f"[[ {ap['name']} [{ap['model']}]] from: {floorPlanGetter(ap['location']['floorPlanId'])} ] renamed to {new_AP_name} {ap['location']['coord']['x_group']},{ap['location']['coord']['y_group']}")

                ap['name'] = new_AP_name
                apSeqNum += 1


            # Convert modified list back into dictionary
            sorted_accessPointsJSON_dict = {'accessPoints': accessPointsLIST_SORTED}
            # print(sorted_accessPointsJSON_dict)

            # save the modified dictionary as accessPoints.json
            with open("accessPoints.json", "w") as outfile:
                json.dump(sorted_accessPointsJSON_dict, outfile, indent=4)

            # move modified accessPoints.json into unpacked folder OVERWRITING ORIGINAL
            shutil.move('accessPoints.json', Path(project_name) / 'accessPoints.json')

            output_esx = Path(project_name + '_re-zip')

            try:
                shutil.make_archive(str(output_esx), 'zip', project_name)
                shutil.move(output_esx.with_suffix('.zip'), output_esx.with_suffix('.esx'))
                print(f'{nl}Process complete {output_esx} re-bundled{nl}')
            except Exception as e:
                print(e)


if __name__ == "__main__":
    start_time = time.time()
    main()
    run_time = time.time() - start_time
    print(f'** Time to run: {round(run_time, 2)} seconds **')
