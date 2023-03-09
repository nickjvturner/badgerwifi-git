#!/usr/bin/env python3

"""
Created by Nick Turner (@nickjvturner)


"""

import zipfile
import json
import shutil
import time
from pathlib import Path
from PIL import Image, ImageDraw
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

            def floorPlanGetter(floorPlanId):
                # print(floorPlansDict.get(floorPlanId))
                return floorPlansDict.get(floorPlanId)

            # by floor name(floorPlanId lookup), tag:value(filtered within tagKeyGetter) and x coord
            accessPointsLIST_SORTED = sorted(accessPointsLIST,
                                             key=lambda i: (floorPlanGetter(i['location']['floorPlanId']),
                                                            i['location']['coord']['x']))

            # Open the image file
            image = Image.open("/Users/nick/Dropbox/Development/badgerwifi-ekahau/ESX/zoom-per-AP/01 First_blank.png")

            # Create an ImageDraw object
            draw = ImageDraw.Draw(image)

            # configure PIL parameters
            x_size = 40
            line_thickness = 8
            circle_radius = x_size + 30
            crop_size = 2000


            for ap in accessPointsLIST_SORTED:
                print(f"[[ {ap['name']} [{ap['model']}]] from: {floorPlanGetter(ap['location']['floorPlanId'])} ]"\
                      f"has coordinates {ap['location']['coord']['x']}, {ap['location']['coord']['y']} {nl}{nl}")

                # establish x and y
                x, y = (ap['location']['coord']['x'], ap['location']['coord']['y'])

                print(x)
                print(y)

                # Draw the X at the specified x, y coordinates
                draw.line((x - x_size, y - x_size, x + x_size, y + x_size), fill="red", width=line_thickness)
                draw.line((x - x_size, y + x_size, x + x_size, y - x_size), fill="red", width=line_thickness)

                # Draw the circle around the X
                draw.ellipse((x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius),
                             outline='red', width=line_thickness)

                # Calculate the crop box for the new image
                crop_box = (x - crop_size // 2, y - crop_size // 2, x + crop_size // 2, y + crop_size // 2)

                # Crop the image
                cropped_image = image.crop(crop_box)

                # Save the cropped image with a new filename
                cropped_image.save(f"/Users/nick/Dropbox/Development/badgerwifi-ekahau/ESX/zoom-per-AP/{ap['name']} - zoomed.jpg")

            # Save the modified image
            image.save("/Users/nick/Dropbox/Development/badgerwifi-ekahau/ESX/zoom-per-AP/EDIT.png")






            # print(accessPointsLIST_SORTED)

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
