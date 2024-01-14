#!/usr/bin/env python3

"""
Script opens up an Ekahau project file discovered in the same directory as the script
Creates an Ekahau style AP placement map
    + Allows you the user to adjust the size in pixels of the AP icon
    + AP icon is slightly transparent allowing installers to see more of the underlying map image
    + Directional arrows will only appear on APs that have been rotated or are "pole" mounted
    + AP name text labels will keep out of the way of directional arrows
Exports blank versions of the map images
Creates a "zoomed" per AP image where other APs are faded by a configurable value
    + For use in per AP installer documentation

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

# Process ONLY specific floor within the project file?
process_specific_floor = False  # True or False
specific_floor = '00 Ground'  # Specify floor name to be processed

# Static PIL Parameters
CROP_SIZE = 1200  # Size of zoomed AP output
RECT_TEXT_OFFSET = 15  # gap between text and box edge
EDGE_BUFFER = 80  # gap between rounded rectangle and cropped image edge
ICON_RESIZE = 200  # Absolute AP icon size in pixels
OPACITY = 0.5  # Value from 0 -> 1, defines the opacity of the 'other' APs on zoomed AP images

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
def createDirectory(new_dir):
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
    if 'bitmapImageId' in floor:
        print(f'bitmapImageId detected, floor plan source probably vector')
        return floor['bitmapImageId']

    else:
        return floor['imageId']


def get_AP_Color(ap):
    if 'color' in ap:
        return ap['color']

    else:
        return '#FFFFFF'


def get_AP_Icon(ap_color_hex, icon_resize, assets_dir):
    ap_color = ekahau_color_dict[ap_color_hex]

    # Import ekahau style custom
    spot = Image.open(assets_dir / f'ekahau-AP-{ap_color}.png')

    return spot.resize((icon_resize, icon_resize))


def get_y_Offset(arrow, angle):
    arrow_length = arrow.height / 2
    default_y_offset = arrow.height / 4

    # Adjacent edge distance is the vertical distance between arrow head and AP icon centre
    adjacent = arrow_length * math.cos(math.radians(angle))

    if adjacent > 0 or abs(adjacent) < default_y_offset:
        return default_y_offset

    else:
        return abs(adjacent) + (arrow_length / 40)


def main():
    font = setFont()

    def floorPlanGetter(floorPlanId):
        # print(floorPlansDict.get(floorPlanId))
        return floorPlansDict.get(floorPlanId)

    def textWidthAndHeightGetter(text):
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
            cropped_blank_map = source_floorPlan_image.copy()
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

            # Load the accessPoints.json file into the accessPoints dictionary
            with open(Path(project_name) / 'accessPoints.json') as json_file:
                accessPoints = json.load(json_file)
            # pprint(accessPoints)

            # Create directory to hold output directories
            createDirectory(Path.cwd() / 'OUTPUT')

            # Create subdirectory for Blank floor plans
            plain_floorplan_destination = Path.cwd() / 'OUTPUT' / 'blank'
            createDirectory(plain_floorplan_destination)

            # Create subdirectory for 'faded zoomed AP' images
            zoom_faded_AP_destination = Path.cwd() / 'OUTPUT' / 'zoom-faded-APs'
            createDirectory(zoom_faded_AP_destination)

            # Create subdirectory for Annotated floorplans
            annotated_floorplan_destination = Path.cwd() / 'OUTPUT' / 'annotated'
            createDirectory(annotated_floorplan_destination)

            # Create subdirectory for temporary files
            tempfile_destination = Path.cwd() / 'OUTPUT' / 'temp'
            createDirectory(tempfile_destination)

            # Define assets directory path
            assets_dir = Path.cwd().parent.parent / 'assets' / 'ekahau_style'

            def annotateMap(map_image, ap):
                font = setFont()

                ap_color = get_AP_Color(ap)

                # establish x and y
                x, y = (ap['location']['coord']['x'] * scaling_ratio,
                        ap['location']['coord']['y'] * scaling_ratio)

                print(
                    f"{nl}[[ {ap['name']} [{ap['model']}]] from: {floorPlanGetter(ap['location']['floorPlanId'])} ] "
                    f"has color '{ekahau_color_dict[ap_color]}' ({ap_color}) and coordinates {x}, {y}")

                spot = get_AP_Icon(get_AP_Color(ap), ICON_RESIZE, assets_dir)

                angle = simulatedRadioDict[ap['id']]['antennaDirection']

                arrow = Image.open(assets_dir / 'ekahau-AP-arrow.png')
                arrow = arrow.resize((ICON_RESIZE, ICON_RESIZE))

                # Calculate AP icon rounded rectangle offset value for text below the AP icon
                y_offset = get_y_Offset(arrow, angle)

                # Define the centre point of the spot
                spot_centre_point = (spot.width // 2, spot.height // 2)

                # Calculate the top-left corner of the icon based on the center point and x, y
                top_left = (int(x) - spot_centre_point[0], int(y) - spot_centre_point[1])

                # Paste the arrow onto the floor plan at the calculated location
                map_image.paste(spot, top_left, mask=spot)

                antenna_mounting = simulatedRadioDict[ap['id']]['antennaMounting']

                if angle != 0.0 or antenna_mounting == 'WALL':
                    print(f'AP has rotational angle of: {angle}')

                    rotated_arrow = arrow.rotate(-angle, expand=True)

                    # Define the centre point of the rotated icon
                    rotated_arrow_centre_point = (rotated_arrow.width // 2, rotated_arrow.height // 2)

                    # Calculate the top-left corner of the icon based on the center point and x, y
                    top_left = (int(x) - rotated_arrow_centre_point[0], int(y) - rotated_arrow_centre_point[1])

                    # draw the rotated arrow onto the floorplan
                    map_image.paste(rotated_arrow, top_left, mask=rotated_arrow)

                # Calculate the height and width of the AP Name rounded rectangle
                text_width, text_height = textWidthAndHeightGetter(ap['name'])

                # Establish coordinates for the rounded rectangle
                x1 = x - (text_width / 2) - RECT_TEXT_OFFSET
                y1 = y + y_offset

                x2 = x + (text_width / 2) + RECT_TEXT_OFFSET
                y2 = y + y_offset + text_height + (RECT_TEXT_OFFSET * 2)

                r = (y2 - y1) / 3

                # Create ImageDraw object for ALL APs Placement map
                draw_map_image = ImageDraw.Draw(map_image)

                # draw the rounded rectangle for "AP Name"
                draw_map_image.rounded_rectangle((x1, y1, x2, y2), r, fill='white', outline='black', width=2)

                # draw the text for "AP Name"
                draw_map_image.text((x, y + y_offset + RECT_TEXT_OFFSET), ap['name'], anchor='mt', fill='black', font=font)

                return map_image

            def crop_map(map_image, ap):
                map_image = annotateMap(map_image, ap)  # Re-annotate the map_image

                # establish x and y
                x, y = (ap['location']['coord']['x'] * scaling_ratio,
                        ap['location']['coord']['y'] * scaling_ratio)

                # Calculate the crop box for the new image
                crop_box = (x - CROP_SIZE // 2, y - CROP_SIZE // 2, x + CROP_SIZE // 2, y + CROP_SIZE // 2)

                # Crop the image
                cropped_map_image = map_image.crop(crop_box)

                # Save the cropped image with a new filename
                cropped_map_image.save(Path(zoom_faded_AP_destination / (ap['name'] + '-zoomed')).with_suffix('.png'))


            for floor in floorPlans['floorPlans']:
                # Optional filter code to process a single specific floor, mostly for testing purposes
                if process_specific_floor:
                    if floor['name'] != specific_floor:
                        continue

                floor_id = vectorSourceCheck(floor)

                # Extract floor plan
                shutil.copy((Path(project_name) / ('image-' + floor_id)), tempfile_destination / floor_id)

                # Open the floor plan to be used for AP placement activities
                source_floorPlan_image = Image.open(tempfile_destination / floor_id)

                map_cropped_within_Ekahau, scaling_ratio, crop_bitmap = cropAssesment()

                APs_on_this_floor = []

                for ap in sorted(accessPoints['accessPoints'], key=lambda i: i['name']):
                    # print(ap)
                    # print(ap['location']['floorPlanId'])
                    if ap['location']['floorPlanId'] == floor['id']:
                        APs_on_this_floor.append(ap)

                current_map_image = source_floorPlan_image.copy()

                # Generate the all_APs map
                for ap in APs_on_this_floor:
                    all_APs = annotateMap(current_map_image, ap)

                # Zoom faded AP map generation
                all_APs_faded = all_APs.copy().convert('RGBA')
                faded_AP_background_map_image = source_floorPlan_image.convert('RGBA')

                all_APs_faded = Image.alpha_composite(faded_AP_background_map_image, Image.blend(faded_AP_background_map_image, all_APs_faded, OPACITY))

                for ap in APs_on_this_floor:
                    crop_map(all_APs_faded.copy(), ap)

                # If map was cropped within Ekahau, crop the all_AP map
                if map_cropped_within_Ekahau:
                    all_APs = all_APs.crop(crop_bitmap)

                # Save the output images
                all_APs.save(Path(annotated_floorplan_destination / floor['name']).with_suffix('.png'))
                # all_APs_faded_map_name = f"{floor['name']}_FADED"
                # all_APs_faded.save(Path(annotated_floorplan_destination / all_APs_faded_map_name).with_suffix('.png'))

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
