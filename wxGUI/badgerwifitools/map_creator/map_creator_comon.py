# map_creator_comon.py

import os
import wx
import math
import shutil
import platform
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from common import ekahau_color_dict
from common import model_antenna_split

from common import FIVE_GHZ_RADIO_ID

# Static PIL Parameters
RECT_TEXT_OFFSET = 15  # gap between text and box edge
EDGE_BUFFER = 80  # gap between rounded rectangle and cropped image edge
OPACITY = 0.5  # Value from 0 -> 1, defines the opacity of the 'other' APs on zoomed AP images

# Define assets directory path
ASSETS_DIR = Path(__file__).parent / 'assets'


def set_font():
    # Define text, font and size
    if platform.system() == "Windows":
        font_path = os.path.join(os.environ["SystemRoot"], "Fonts", "Consola.ttf")
        return ImageFont.truetype(font_path, 30)
    else:
        return ImageFont.truetype("Menlo.ttc", 30)


def vector_source_check(floor, message_callback):
    # Check if the floor plan is a vector or bitmap image
    if 'bitmapImageId' in floor:
        wx.CallAfter(message_callback, f"bitmapImageId detected, source floor plan image is probably a vector")
        return floor['bitmapImageId']
    else:
        return floor['imageId']


def get_ap_icon(ap, custom_ap_icon_size):
    # Get the AP icon colour
    ap_color_hex = ap.get('color', '#FFFFFF')
    ap_color = ekahau_color_dict.get(ap_color_hex)

    # Import ekahau style custom
    spot = Image.open(ASSETS_DIR / 'ekahau_style' / f'ekahau-AP-{ap_color}.png')

    return spot.resize((custom_ap_icon_size, custom_ap_icon_size))


def get_y_offset(arrow, angle):
    arrow_length = arrow.height / 2
    default_y_offset = arrow.height / 4

    # Adjacent edge distance is the vertical distance between arrow head and AP icon centre
    adjacent = arrow_length * math.cos(math.radians(angle))

    if adjacent > 0 or abs(adjacent) < default_y_offset:
        return default_y_offset

    else:
        return abs(adjacent) + (arrow_length / 40)


def text_width_and_height_getter(text):
    font = set_font()

    # Create a working space image and draw object
    working_space = Image.new("RGB", (500, 500), color="white")
    draw = ImageDraw.Draw(working_space)

    # Draw the text onto the image and get its bounding box
    text_box = draw.textbbox((0, 0), text, font=font, spacing=4, align="center")

    # Width and height of the bounding box
    width = text_box[2] - text_box[0]
    height = text_box[3] - text_box[1]

    return width, height


def crop_assessment(floor, source_floor_plan_image, project_dir, floor_id, blank_plan_dir):
    # Check if the floor plan has been cropped within Ekahau?
    crop_bitmap = (floor['cropMinX'], floor['cropMinY'], floor['cropMaxX'], floor['cropMaxY'])

    # Calculate scaling ratio
    scaling_ratio = source_floor_plan_image.width / floor['width']

    if crop_bitmap[0] != 0.0 or crop_bitmap[1] != 0.0 or crop_bitmap[2] != floor['width'] or crop_bitmap[3] != floor['height']:
        # Calculate x,y coordinates of the crop within Ekahau
        crop_bitmap = (crop_bitmap[0] * scaling_ratio,
                       crop_bitmap[1] * scaling_ratio,
                       crop_bitmap[2] * scaling_ratio,
                       crop_bitmap[3] * scaling_ratio)

        # save a blank copy of the cropped floorplan
        cropped_blank_map = source_floor_plan_image.copy()
        cropped_blank_map = cropped_blank_map.crop(crop_bitmap)
        cropped_blank_map.save(Path(blank_plan_dir / floor['name']).with_suffix('.png'))

        # set boolean value
        map_cropped_within_ekahau = True

        return map_cropped_within_ekahau, scaling_ratio, crop_bitmap

    else:
        # There is no crop within Ekahau
        # set boolean value
        map_cropped_within_ekahau = False

        # save a blank copy of the floor plan
        shutil.copy(project_dir / ('image-' + floor_id), Path(blank_plan_dir / floor['name']).with_suffix('.png'))

        return map_cropped_within_ekahau, scaling_ratio, None


def annotate_map(map_image, ap, scaling_ratio, custom_ap_icon_size, simulated_radio_dict, message_callback, floor_plans_dict):
    font = set_font()

    ap_color = ap['color'] if 'color' in ap else 'FFFFFF'

    # establish x and y
    x, y = (ap['location']['coord']['x'] * scaling_ratio,
            ap['location']['coord']['y'] * scaling_ratio)

    wx.CallAfter(message_callback, f"{ap['name']} ({model_antenna_split(ap['model'])[0]}) ][ {floor_plans_dict.get(ap['location']['floorPlanId'])} ][ colour: '{ekahau_color_dict.get(ap_color)}' ][ coordinates {round(x)}, {round(y)}")

    spot = get_ap_icon(ap, custom_ap_icon_size)

    angle = simulated_radio_dict[ap['id']][FIVE_GHZ_RADIO_ID]['antennaDirection']

    arrow = Image.open(ASSETS_DIR / 'ekahau_style' / 'ekahau-AP-arrow.png')
    arrow = arrow.resize((custom_ap_icon_size, custom_ap_icon_size))

    # Calculate AP icon rounded rectangle offset value for text below the AP icon
    y_offset = get_y_offset(arrow, angle)

    # Define the centre point of the spot
    spot_centre_point = (spot.width // 2, spot.height // 2)

    # Calculate the top-left corner of the icon based on the center point and x, y
    top_left = (int(x) - spot_centre_point[0], int(y) - spot_centre_point[1])

    # Paste the arrow onto the floor plan at the calculated location
    map_image.paste(spot, top_left, mask=spot)

    antenna_mounting = simulated_radio_dict[ap['id']][FIVE_GHZ_RADIO_ID]['antennaMounting']

    if angle != 0.0 or antenna_mounting == 'WALL':
        wx.CallAfter(message_callback, f'AP has rotational angle of: {round(angle)}')

        rotated_arrow = arrow.rotate(-angle, expand=True)

        # Define the centre point of the rotated icon
        rotated_arrow_centre_point = (rotated_arrow.width // 2, rotated_arrow.height // 2)

        # Calculate the top-left corner of the icon based on the center point and x, y
        top_left = (int(x) - rotated_arrow_centre_point[0], int(y) - rotated_arrow_centre_point[1])

        # draw the rotated arrow onto the floor plan
        map_image.paste(rotated_arrow, top_left, mask=rotated_arrow)

    # Calculate the height and width of the AP Name rounded rectangle
    text_width, text_height = text_width_and_height_getter(ap['name'])

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


def crop_map(map_image, ap, scaling_ratio, zoomed_ap_crop_size):

    # establish x and y
    x, y = (ap['location']['coord']['x'] * scaling_ratio,
            ap['location']['coord']['y'] * scaling_ratio)

    # Calculate the crop box for the new image
    crop_box = (x - zoomed_ap_crop_size // 2, y - zoomed_ap_crop_size // 2, x + zoomed_ap_crop_size // 2, y + zoomed_ap_crop_size // 2)

    # Crop the image
    cropped_map_image = map_image.crop(crop_box)

    return cropped_map_image


def annotate_pds_map(map_image, ap, scaling_ratio, custom_ap_icon_size, message_callback, floor_plans_dict):
    font = set_font()

    # establish x and y
    x, y = (ap['location']['coord']['x'] * scaling_ratio,
            ap['location']['coord']['y'] * scaling_ratio)

    wx.CallAfter(message_callback,
        f"{ap['name']} ({model_antenna_split(ap['model'])[0]}) ][ {floor_plans_dict.get(ap['location']['floorPlanId'])} ][ coordinates {round(x)}, {round(y)}")

    spot = Image.open(ASSETS_DIR / 'custom' / 'spot.png')
    spot = spot.resize((custom_ap_icon_size, custom_ap_icon_size))

    # Calculate AP icon rounded rectangle offset value for text below the AP icon
    y_offset = (custom_ap_icon_size / 3)

    # Define the centre point of the spot
    spot_centre_point = (spot.width // 2, spot.height // 2)

    # Calculate the top-left corner of the icon based on the center point and x, y
    top_left = (int(x) - spot_centre_point[0], int(y) - spot_centre_point[1])

    # Paste the arrow onto the floor plan at the calculated location
    map_image.paste(spot, top_left, mask=spot)

    # Calculate the height and width of the AP Name rounded rectangle
    text_width, text_height = text_width_and_height_getter(ap['name'])

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
