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
import math
# from pprint import pprint

# Process specific floor within the project file?
process_specific_floor = False  # True or False
specific_floor = '00 Ground'  # Specify floor name to be processed

# Static PIL Parameters
crop_size = 1200  # Size of zoomed AP output
text_rect_offset = 15  # gap between text and box edge
edge_buffer = 80  # gap between cropped image edge and rounded rectangle
r = 20  # Corner radius
icon_resize = 200  # Absolute AP icon size in pixels

# Variables
nl = '\n'

ekahau_color_dict = {
    '#00FF00': 'green',
    '#FFE600': 'yellow',
    '#FF8500': 'orange',
    '#FF0000': 'red',
    '#FF00FF': 'pink',
    '#C297FF': 'violet',
    '#0068FF': 'blue',
    '#6D6D6D': 'gray',
    '#FFFFFF': 'default',
    '#C97700': 'brown',
    '#00FFCE': 'mint'
}


# Functions
def create_directory(new_dir):
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
        return f'Directory {new_dir} Created'
    else:
        return f'Directory {new_dir} already exists'


def setFont():
    # Define text, font and size
    if platform.system() == "Windows":
        font_path = os.path.join(os.environ["SystemRoot"], "Fonts", "Consola.ttf")
        return ImageFont.truetype(font_path, 30)
    else:
        return ImageFont.truetype("Menlo.ttc", 30)


def vectorSourceCheck(floor):
    # Check if floorplan source was .dwg, by checking if bitmapImageId exists
    try:
        floor_id = floor['bitmapImageId']
        print(f'bitmapImageId detected, floor plan source probably vector')
        return floor_id

    except Exception:
        return floor['imageId']


def get_AP_color(ap):
    if 'color' in ap:
        return ap['color']

    else:
        return '#FFFFFF'


def get_AP_icon(ap_color_hex, icon_resize, assets_dir):
    ap_color = ekahau_color_dict[ap_color_hex]

    # Import ekahau style custom
    spot = Image.open(assets_dir / f'ekahau-AP-{ap_color}.png')

    return spot.resize((icon_resize, icon_resize))


def get_y_offset(arrow, angle):
    arrow_length = arrow.height / 2
    default_y_offset = arrow.height / 4

    # Adjacent edge distance is the vertical distance between arrow head and AP icon centre
    adjacent = arrow_length * math.cos(math.radians(angle))

    if adjacent > 0 or abs(adjacent) < default_y_offset:
        return default_y_offset

    else:
        return abs(adjacent) + (arrow_length / 40)


def main():
    def floorPlanGetter(floorPlanId):
        # print(floorPlansDict.get(floorPlanId))
        return floorPlansDict.get(floorPlanId)

    def text_width_and_height_getter(text):
        # Create a working space image and draw object
        working_space = Image.new("RGB", (500, 500), color="white")
        draw = ImageDraw.Draw(working_space)

        # Draw the text onto the image and get its bounding box
        text_box = draw.textbbox((0, 0), text, font=font, spacing=4, align="center")

        # Print the width and height of the bounding box
        width = text_box[2] - text_box[0]
        height = text_box[3] - text_box[1]

        return width, height

    def cropAssesment():
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

            return map_cropped_within_Ekahau, scaling_ratio, crop_bitmap

        else:
            # There is no crop
            scaling_ratio = 1

            # set boolean value
            map_cropped_within_Ekahau = False

            # save a blank copy of the floorplan
            shutil.copy((Path(project_name) / ('image-' + floor_id)),
                        Path(plain_floorplan_destination / floor['name']).with_suffix('.png'))

            return map_cropped_within_Ekahau, scaling_ratio, None

    # Get filename and current working directory
    print(f'{nl}{Path(__file__).name}')
    print(f'working_directory: {Path.cwd()}{nl}')

    # Get local file with extension .esx
    for file in sorted(Path.cwd().iterdir()):
        # ignore files in directory containing _re-zip
        if (file.suffix == '.esx') and (not ('re-zip' in file.stem)):
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

            # Load the simulatedRadios.json file into the simulatedRadios dictionary
            with open(Path(project_name) / 'simulatedRadios.json') as json_file:
                simulatedRadios = json.load(json_file)
            # pprint(simulatedRadios)

            # Create an intermediary dictionary to lookup simulated radio parameters
            simulatedRadioDict = {}

            # Populate the intermediary dictionary
            for radio in simulatedRadios['simulatedRadios']:
                simulatedRadioDict[radio['accessPointId']] = {}  # initialize nested dictionary
                for x, y in radio.items():
                    # print(x, y)
                    simulatedRadioDict[radio['accessPointId']][x] = y

            # pprint(simulatedRadioDict)
            # print(simulatedRadioDict['84d58cfc-1121-4b8c-97e7-c589f56494e4']['antennaHeight'])

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

            # Create subdirectory for temporary files
            tempfile_destination = Path.cwd() / 'OUTPUT' / 'temp'
            create_directory(tempfile_destination)

            # Define assets directory path
            assets_dir = Path.cwd().parent.parent / 'assets' / 'ekahau_style'

            arrow = Image.open(assets_dir / 'ekahau-AP-arrow.png')
            arrow = arrow.resize((icon_resize, icon_resize))

            font = setFont()

            for floor in floorPlans['floorPlans']:
                if process_specific_floor:
                    if floor['name'] != specific_floor:
                        continue

                floor_id = vectorSourceCheck(floor)

                # Extract floorplan
                shutil.copy((Path(project_name) / ('image-' + floor_id)), tempfile_destination / floor_id)

                # Open the floorplan to be used for all AP placement
                all_APs = Image.open(tempfile_destination / floor_id)

                map_cropped_within_Ekahau, scaling_ratio, crop_bitmap = cropAssesment()

                # Create ImageDraw object for all APs map
                draw_all_APs = ImageDraw.Draw(all_APs)

                for ap in sorted(accessPoints['accessPoints'], key=lambda i: i['name']):
                    # print(ap)
                    # print(ap['location']['floorPlanId'])
                    if ap['location']['floorPlanId'] == floor['id']:
                        ap_color = get_AP_color(ap)

                        try:
                            # establish x and y
                            x, y = (ap['location']['coord']['x'] * scaling_ratio, ap['location']['coord']['y'] * scaling_ratio)

                            print(
                                f"{nl}[[ {ap['name']} [{ap['model']}]] from: {floorPlanGetter(ap['location']['floorPlanId'])} ] "
                                f"has color '{ekahau_color_dict[ap_color]}' ({ap_color}) and coordinates {x}, {y}")

                        except Exception:
                            print(f"no x, y coordinates found for {ap['name']}, this AP is not placed on a map... skipping AP")
                            continue

                        # Open the floorplan to be used for isolated AP image
                        isolated_AP = Image.open(tempfile_destination / floor_id)

                        # Create ImageDraw object for isolated AP image
                        draw_isolated_AP = ImageDraw.Draw(isolated_AP)

                        spot = get_AP_icon(ap_color, icon_resize, assets_dir)

                        angle = simulatedRadioDict[ap['id']]['antennaDirection']
                        print(f'AP has rotational angle of: {angle}')

                        # set simulatedRadio variables
                        antennaTilt = simulatedRadioDict[ap['id']]['antennaTilt']
                        antennaMounting = simulatedRadioDict[ap['id']]['antennaMounting']
                        antennaHeight = simulatedRadioDict[ap['id']]['antennaHeight']

                        plans = (all_APs, isolated_AP)

                        # Calculate AP icon rounded rectangle offset value for text below the AP icon
                        y_offset = get_y_offset(arrow, angle)

                        # Define the centre point of the spot
                        spot_centre_point = (spot.width // 2, spot.height // 2)

                        # Calculate the top-left corner of the icon based on the center point and x, y
                        top_left = (int(x) - spot_centre_point[0], int(y) - spot_centre_point[1])

                        for plan in plans:
                            # Paste the arrow onto the floorplan at the calculated location
                            plan.paste(spot, top_left, mask=spot)

                        if angle != 0.0 or ap_color == '#FF0000':
                            rotated_arrow = arrow.rotate(-angle, expand=True)

                            # Define the centre point of the rotated icon
                            rotated_arrow_centre_point = (rotated_arrow.width // 2, rotated_arrow.height // 2)

                            # Calculate the top-left corner of the icon based on the center point and x, y
                            top_left = (int(x) - rotated_arrow_centre_point[0], int(y) - rotated_arrow_centre_point[1])

                            # draw the rotated arrow onto the floorplan
                            for plan in plans:
                                plan.paste(rotated_arrow, top_left, mask=rotated_arrow)

                        # Calculate the height and width of the AP Name rounded rectangle
                        text_width, text_height = text_width_and_height_getter(ap['name'])

                        # Establish coordinates for the rounded rectangle
                        x1 = x - (text_width / 2) - text_rect_offset
                        y1 = y + y_offset

                        x2 = x + (text_width / 2) + text_rect_offset
                        y2 = y + y_offset + text_height + (text_rect_offset * 2)

                        r = (y2 - y1) / 3

                        # draw the rounded rectangle for "AP Name"
                        draw_all_APs.rounded_rectangle((x1, y1, x2, y2), r, fill='white', outline='black', width=2)
                        draw_isolated_AP.rounded_rectangle((x1, y1, x2, y2), r, fill='white', outline='black', width=2)

                        # draw the text for "AP Name"
                        draw_all_APs.text((x, y + y_offset + text_rect_offset), ap['name'], anchor='mt', fill='black', font=font)
                        draw_isolated_AP.text((x, y + y_offset + text_rect_offset), ap['name'], anchor='mt', fill='black', font=font)


                        # Calculate the crop box for the new image
                        crop_box = (x - crop_size // 2, y - crop_size // 2, x + crop_size // 2, y + crop_size // 2)

                        # Crop the image
                        cropped_image = isolated_AP.crop(crop_box)

                        # create ImageDraw object for isolated AP
                        draw_isolated_AP = ImageDraw.Draw(cropped_image)

                        # Save the cropped image with a new filename
                        cropped_image.save(Path(zoomed_AP_destination / (ap['name'] + '-zoomed')).with_suffix('.png'))

                # If map was cropped within Ekahau, crop the all_AP map
                if map_cropped_within_Ekahau:
                    all_APs = all_APs.crop(crop_bitmap)

                # Save the modified image
                all_APs.save(Path(annotated_floorplan_destination / floor['name']).with_suffix('.png'))

            try:
                shutil.rmtree(project_name)
                shutil.rmtree(tempfile_destination)
                print(f'Temporary project contents directory removed{nl}')
            except Exception as e:
                print(e)


if __name__ == "__main__":
    start_time = time.time()
    main()
    run_time = time.time() - start_time
    print(f'** Time to run: {round(run_time, 2)} seconds **')
