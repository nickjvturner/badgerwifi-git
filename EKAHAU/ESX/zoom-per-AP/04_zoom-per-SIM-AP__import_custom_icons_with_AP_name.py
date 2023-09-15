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

            # Load the simulatedRadios.json file into the simulatedRadios dictionary
            with open(Path(project_name) / 'simulatedRadios.json') as json_file:
                simulatedRadios = json.load(json_file)
            # pprint(simulatedRadios)

            # Create an intermediary dictionary to lookup AP radio parameters
            apDirectionDict = {}

            # Populate the intermediary dictionary
            for radio in simulatedRadios['simulatedRadios']:
                # print(radio)
                # print(radio['accessPointId'])
                # print(radio['antennaDirection'])
                apDirectionDict[radio['accessPointId']] = radio['antennaDirection']
            # pprint(apDirectionDict)

            def apDirectionGetter(accessPointId):
                # print(floorPlansDict.get(floorPlanId))
                return apDirectionDict.get(accessPointId)

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

            # Define assets directory path
            assets_dir = Path.cwd() / 'assets'

            # Import custom icons
            arrow = Image.open(assets_dir / 'arrow.png')
            spot = Image.open(assets_dir / 'spot.png')

            # Resize icons if necessary (default size is 350x350 px)
            icon_resize = 200

            arrow = arrow.resize((icon_resize, icon_resize))
            spot = spot.resize((icon_resize, icon_resize))

            # PIL Parameters
            crop_size = 1200
            offset = 10

            # Define text, font and size
            if platform.system() == "Windows":
                font_path = os.path.join(os.environ["SystemRoot"], "Fonts", "Consola.ttf")
                font = ImageFont.truetype(font_path, 30)
            else:
                font = ImageFont.truetype("Menlo.ttc", 30)

            for floor in floorPlans['floorPlans']:
                # If the floorplan source file was .dwg we need to reference the bitmapImageId instead of imageId
                try:
                    floor_id = floor['bitmapImageId']
                except Exception as e:
                    floor_id = floor['imageId']

                # Extract floorplans
                shutil.copy((Path(project_name) / ('image-' + floor_id)), floor_id)

                # Open the floorplan to be used for all AP placement
                all_APs = Image.open(floor_id)

                # is the floorplan cropped?
                crop_bitmap = (floor['cropMinX'], floor['cropMinY'], floor['cropMaxX'], floor['cropMaxY'])

                if crop_bitmap[0] != 0.0 or crop_bitmap[1] != 0.0:
                    scaling_ratio = all_APs.width / floor['width']
                    crop_bitmap = (crop_bitmap[0] * scaling_ratio, crop_bitmap[1] * scaling_ratio, crop_bitmap[2] * scaling_ratio, crop_bitmap[3] * scaling_ratio)
                    map_cropped_within_Ekahau = True
                    cropped_blank_map = all_APs.copy()
                    cropped_blank_map = cropped_blank_map.crop(crop_bitmap)
                    cropped_blank_map.save(Path(plain_floorplan_destination / floor['name']).with_suffix('.png'))

                else:
                    scaling_ratio = 1
                    map_cropped_within_Ekahau = False
                    # save blank copy
                    shutil.copy((Path(project_name) / ('image-' + floor_id)), Path(plain_floorplan_destination / floor['name']).with_suffix('.png'))

                # Create ImageDraw object
                draw_all_APs = ImageDraw.Draw(all_APs)

                for ap in accessPoints['accessPoints']:
                    # print(ap['location']['floorPlanId'])
                    if ap['location']['floorPlanId'] == floor['id']:

                        # establish x and y
                        x, y = (ap['location']['coord']['x'] * scaling_ratio, ap['location']['coord']['y'] * scaling_ratio)

                        print(
                            f"{nl}[[ {ap['name']} [{ap['model']}]] from: {floorPlanGetter(ap['location']['floorPlanId'])} ] "
                            f"has coordinates {x}, {y}")

                        # Open the floorplan to be used for isolated AP image
                        isolated_AP = Image.open(floor_id)

                        # Create ImageDraw object
                        draw_isolated_AP = ImageDraw.Draw(isolated_AP)

                        angle = apDirectionGetter(ap['id'])
                        print(f'AP has rotational angle of: {angle}')

                        plans = (all_APs, isolated_AP)
                        draw_objects = (draw_all_APs, draw_isolated_AP)

                        if angle != 0.0:
                            rotated_arrow = arrow.rotate(-angle, expand=True)

                            # Define the centre point of the rotated icon
                            rotated_arrow_centre_point = (rotated_arrow.width // 2, rotated_arrow.height // 2)

                            # Calculate the top-left corner of the icon based on the center point and x, y
                            top_left = (int(x) - rotated_arrow_centre_point[0], int(y) - rotated_arrow_centre_point[1])

                            deviation = 30

                            if (180 - deviation) < angle < (180 + deviation):
                                # Override y_offsetter the text below the AP icon
                                y_offsetter = arrow.height / 1.9

                            for plan in plans:
                                plan.paste(rotated_arrow, top_left, mask=rotated_arrow)

                        else:
                            # Define the centre point of the icon
                            arrow_centre_point = (arrow.width // 2, arrow.height // 2)

                            # Calculate the top-left corner of the icon based on the center point and x, y
                            top_left = (int(x) - arrow_centre_point[0], int(y) - arrow_centre_point[1])

                            for plan in plans:
                                # Paste the spot onto the floorplan at the calculated location
                                plan.paste(spot, top_left, mask=spot)

                            # Offset the text below the AP icon
                            y_offsetter = arrow.height / 2.5

                        # Define text
                        text = ap['name']

                        # Calculate the width and height of the text
                        text_box = draw_all_APs.textbbox((0, 0, 1000, 1000), text, font=font, spacing=4,
                                                 align="center")

                        text_width = (text_box[2] - text_box[0])
                        text_height = (text_box[3] - text_box[1])

                        # Establish coordinates for the rounded rectangle
                        x1 = x - (text_width / 2) - offset
                        y1 = y + y_offsetter - (text_height / 2) - offset

                        x2 = x + (text_width / 2) + offset
                        y2 = y + y_offsetter + (text_height / 2) + offset

                        r = (y2 - y1) / 3

                        for draw_object in draw_objects:
                            # draw the rounded rectangle
                            draw_object.rounded_rectangle((x1, y1, x2, y2), r, fill='white', outline='black', width=2)

                            # draw the text
                            draw_object.text((x, y + y_offsetter + 2), text, anchor='mm',
                                      fill='black', font=font)

                        # Calculate the crop box for the new image
                        crop_box = (x - crop_size // 2, y - crop_size // 2, x + crop_size // 2, y + crop_size // 2)

                        # Crop the image
                        cropped_image = isolated_AP.crop(crop_box)

                        # Save the cropped image with a new filename
                        cropped_image.save(Path(zoomed_AP_destination / (ap['name'] + '-zoomed')).with_suffix('.png'))

                # Remove raw floorplan source files
                os.remove(floor_id)

                # If map was cropped within Ekahau, crop the all_AP map
                if map_cropped_within_Ekahau:
                    all_APs = all_APs.crop(crop_bitmap)

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
