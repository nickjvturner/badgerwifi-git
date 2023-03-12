#!/usr/bin/env python3

"""
Created by Nick Turner (@nickjvturner)


"""

import os
import zipfile
import json
import shutil
import time
from pathlib import Path
from PIL import Image, ImageDraw
from pprint import pprint


def main():
    def create_directory(new_dir):
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
            return f'Directory {new_dir} Created'
        else:
            return f'Directory {new_dir} already exists'

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
                floorPlans = json.load(json_file)
            # pprint(floorPlans)

            # Create an intermediary dictionary to lookup floor names
            floorPlansDict = {}

            # Populate the intermediary dictionary with {floorId: floor name}
            for floor in floorPlans['floorPlans']:
                floorPlansDict[floor['id']] = floor['name']
            # pprint(floorPlansDict)

            def floorPlanGetter(floorPlanId):
                # print(floorPlansDict.get(floorPlanId))
                return floorPlansDict.get(floorPlanId)

            # Load the accessPoints.json file into the accessPoints dictionary
            with open(Path(project_name) / 'accessPoints.json') as json_file:
                accessPoints = json.load(json_file)
            # pprint(accessPoints)

            # Create directory to hold output directories
            create_directory(Path.cwd() / 'OUTPUT')

            # Create subdirectory for Blank floor plans
            plain_floorplan_destination = Path.cwd() / 'OUTPUT' / 'blank'
            create_directory(plain_floorplan_destination)

            # Create subdirectory for 'zoomed isolated AP' images
            zoomed_AP_destination = Path.cwd() / 'OUTPUT' / 'zoomed-APs'
            create_directory(zoomed_AP_destination)

            # Create subdirectory for Annotated floorplans
            annotated_floorplan_destination = Path.cwd() / 'OUTPUT' / 'annotated'
            create_directory(annotated_floorplan_destination)

            for floor in floorPlans['floorPlans']:
                # Extract floorplans
                shutil.copy((Path(project_name) / ('image-' + floor['imageId'])), Path(plain_floorplan_destination / floor['name']).with_suffix('.png'))
                shutil.copy((Path(project_name) / ('image-' + floor['imageId'])), floor['imageId'])

                # Open the floorplan to be used for all AP placement
                all_APs = Image.open(floor['imageId'])

                # Create an ImageDraw object
                draw_all_APs = ImageDraw.Draw(all_APs)

                # configure PIL parameters
                x_size = 40
                line_thickness = 8
                radius = x_size + 30
                crop_size = 2000

                for ap in accessPoints['accessPoints']:
                    # print(ap['location']['floorPlanId'])
                    if ap['location']['floorPlanId'] == floor['id']:

                        print(f"[[ {ap['name']} [{ap['model']}]] from: {floorPlanGetter(ap['location']['floorPlanId'])} ] "
                              f"has coordinates {ap['location']['coord']['x']}, {ap['location']['coord']['y']} {nl}")

                        # establish x and y
                        x, y = (ap['location']['coord']['x'], ap['location']['coord']['y'])

                        # Open the floorplan to be used for isolated AP image
                        isolated_AP = Image.open(floor['imageId'])

                        # Create ImageDraw object
                        draw_isolated_AP = ImageDraw.Draw(isolated_AP)

                        plans = (draw_all_APs, draw_isolated_AP)

                        for plan in plans:

                            # Draw the X at the specified x, y coordinates
                            plan.line((x - x_size, y - x_size, x + x_size, y + x_size), fill="red", width=line_thickness)
                            plan.line((x - x_size, y + x_size, x + x_size, y - x_size), fill="red", width=line_thickness)

                            # Draw the circle around the X
                            plan.ellipse((x - radius, y - radius, x + radius, y + radius), outline='red', width=line_thickness)

                            # Calculate the crop box for the new image
                            crop_box = (x - crop_size // 2, y - crop_size // 2, x + crop_size // 2, y + crop_size // 2)

                            # Crop the image
                            cropped_image = isolated_AP.crop(crop_box)

                            # Save the cropped image with a new filename
                            cropped_image.save(Path(zoomed_AP_destination / (ap['name'] + '-zoomed')).with_suffix('.png'))

                # Remove raw floorplan source files
                os.remove(floor['imageId'])

                # Save the modified image
                all_APs.save(Path(annotated_floorplan_destination / floor['name']).with_suffix('.png'))

            try:
                shutil.rmtree(project_name)
                print(f'Temporary project contents directory removed{nl}')
            except Exception as e:
                print(e)


if __name__ == "__main__":
    start_time = time.time()
    main()
    run_time = time.time() - start_time
    print(f'** Time to run: {round(run_time, 2)} seconds **')
