#!/usr/bin/env python3

"""
Created by Nick Turner (@nickjvturner)


"""

import os
import zipfile
import json
import shutil
import time
import platform
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
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

            # Create directory to hold output directories
            create_directory(Path.cwd() / 'OUTPUT')

            # Create subdirectory for Blank floor plans
            plain_floorplan_destination = Path.cwd() / 'OUTPUT' / 'blank'
            create_directory(plain_floorplan_destination)

            # Define assets directory path
            assets_dir = Path.cwd() / 'assets'

            # Define text, font and size
            if platform.system() == "Windows":
                font_path = os.path.join(os.environ["SystemRoot"], "Fonts", "Consola.ttf")
                font = ImageFont.truetype(font_path, 30)
            else:
                font = ImageFont.truetype("Menlo.ttc", 30)

            for floor in floorPlans['floorPlans']:
                # Check if floorplan source was .dwg, by checking if bitmapImageId exists
                try:
                    floor_id = floor['bitmapImageId']

                except Exception as e:
                    floor_id = floor['imageId']

                # Extract floorplan
                shutil.copy((Path(project_name) / ('image-' + floor_id)), floor_id)

                # Open the floorplan to be used for all AP placement
                all_APs = Image.open(floor_id)

                # Check if the floorplan has been cropped within Ekahau?
                crop_bitmap = (floor['cropMinX'], floor['cropMinY'], floor['cropMaxX'], floor['cropMaxY'])

                if crop_bitmap[0] != 0.0 or crop_bitmap[1] != 0.0:

                    # Calculate scaling ratio
                    scaling_ratio = all_APs.width / floor['width']

                    # Calculate x,y coordinates of the crop within Ekahau
                    crop_bitmap = (crop_bitmap[0] * scaling_ratio,
                                   crop_bitmap[1] * scaling_ratio,
                                   crop_bitmap[2] * scaling_ratio,
                                   crop_bitmap[3] * scaling_ratio)

                    # set boolean value
                    map_cropped_within_Ekahau = True

                    # save a blank copy of the cropped floorplan
                    cropped_blank_map = all_APs.copy()
                    cropped_blank_map = cropped_blank_map.crop(crop_bitmap)
                    cropped_blank_map.save(Path(plain_floorplan_destination / floor['name']).with_suffix('.png'))

                else:
                    # There is no crop
                    # save a blank copy of the floorplan
                    shutil.copy((Path(project_name) / ('image-' + floor_id)), Path(plain_floorplan_destination / floor['name']).with_suffix('.png'))

                # Remove raw floorplan source files
                os.remove(floor_id)


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
