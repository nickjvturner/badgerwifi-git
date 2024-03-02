#!/usr/bin/env python3

"""
Creates an Ekahau style AP placement map
    + Allows you the user to adjust the size in pixels of the AP icon
    + AP icon is slightly transparent allowing installers to see more of the underlying map image
    + Directional arrows will only appear on APs that have been rotated or are "pole" mounted
    + AP name text labels will keep out of the way of directional arrows

Created by Nick Turner (@nickjvturner)
"""

import os
import shutil
import platform
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math


from common import ekahau_color_dict
from common import load_json
from common import create_floor_plans_dict
from common import create_tag_keys_dict
from common import create_simulated_radios_dict
from common import create_notes_dict

from common import FIVE_GHZ_RADIO_ID

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


def create_ap_location_map(working_directory, project_name, message_callback):

    message_callback(f'performing action for: {project_name}\n')
    project_dir = Path(working_directory) / project_name

    font = setFont()

    def floorPlanGetter(floorPlanId):
        # print(floorPlansDict.get(floorPlanId))
        return floor_plans_dict.get(floorPlanId)

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
            cropped_blank_map.save(Path(blank_plan_dir / floor['name']).with_suffix('.png'))

            return map_cropped_within_Ekahau, scaling_ratio, crop_bitmap

        else:
            # There is no crop
            scaling_ratio = 1

            # set boolean value
            map_cropped_within_Ekahau = False

            # save a blank copy of the floorplan
            shutil.copy(project_dir / ('image-' + floor_id),
                        Path(blank_plan_dir / floor['name']).with_suffix('.png'))

            return map_cropped_within_Ekahau, scaling_ratio, None

    # Load JSON data
    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    access_points_json = load_json(project_dir, 'accessPoints.json', message_callback)
    simulated_radios_json = load_json(project_dir, 'simulatedRadios.json', message_callback)
    tag_keys_json = load_json(project_dir, 'tagKeys.json', message_callback)
    notes_json = load_json(project_dir, 'notes.json', message_callback)

    # Process data
    floor_plans_dict = create_floor_plans_dict(floor_plans_json)
    tag_keys_dict = create_tag_keys_dict(tag_keys_json)
    simulated_radio_dict = create_simulated_radios_dict(simulated_radios_json)
    notes_dict = create_notes_dict(notes_json)


    # Create directory to hold output directories
    output_dir = working_directory / "OUTPUT"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory for Blank floor plans
    blank_plan_dir = output_dir / 'blank'
    blank_plan_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory for 'faded zoomed AP' images
    zoom_faded_dir = output_dir / 'zoom_faded_dir'
    zoom_faded_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory for Annotated floorplans
    annotated_plan_dir = output_dir / 'annotated'
    annotated_plan_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory for temporary files
    temp_dir = output_dir / 'temp'
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Define assets directory path
    assets_dir = Path(__file__).parent / 'assets' / 'ekahau_style'

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

        angle = simulated_radio_dict[ap['id']][FIVE_GHZ_RADIO_ID]['antennaDirection']

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

        antenna_mounting = simulated_radio_dict[ap['id']][FIVE_GHZ_RADIO_ID]['antennaMounting']

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
        cropped_map_image.save(Path(zoom_faded_dir / (ap['name'] + '-zoomed')).with_suffix('.png'))


    for floor in floor_plans_json['floorPlans']:

        floor_id = vectorSourceCheck(floor)

        # Extract floor plan
        shutil.copy(project_dir / ('image-' + floor_id), temp_dir / floor_id)

        # Open the floor plan to be used for AP placement activities
        source_floorPlan_image = Image.open(temp_dir / floor_id)

        map_cropped_within_Ekahau, scaling_ratio, crop_bitmap = cropAssesment()

        APs_on_this_floor = []

        for ap in sorted(access_points_json['accessPoints'], key=lambda i: i['name']):
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
        all_APs.save(Path(annotated_plan_dir / floor['name']).with_suffix('.png'))
        # all_APs_faded_map_name = f"{floor['name']}_FADED"
        # all_APs_faded.save(Path(annotated_floorplan_destination / all_APs_faded_map_name).with_suffix('.png'))

    try:
        # shutil.rmtree(project_name)
        # shutil.rmtree(tempfile_destination)
        print(f'Temporary project contents directory removed{nl}')
    except Exception as e:
        print(e)
