# create_custom_ap_location_maps.py

import wx
import shutil
import threading
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from common import load_json
from common import create_floor_plans_dict
from common import create_simulated_radios_dict

from map_creator.map_creator_comon import vector_source_check
from map_creator.map_creator_comon import crop_assessment
from map_creator.map_creator_comon import annotate_map

from common import FIVE_GHZ_RADIO_ID

# Static PIL Parameters
RECT_TEXT_OFFSET = 15  # gap between text and box edge
EDGE_BUFFER = 80  # gap between rounded rectangle and cropped image edge
OPACITY = 0.5  # Value from 0 -> 1, defines the opacity of the 'other' APs on zoomed AP images

# Variables
nl = '\n'


def create_custom_ap_location_maps_threaded(working_directory, project_name, message_callback, custom_ap_icon_size):
    # Wrapper function to run insert_images in a separate thread
    def run_in_thread():
        create_custom_ap_location_maps(working_directory, project_name, message_callback, custom_ap_icon_size)
    # Start the long-running task in a separate thread
    threading.Thread(target=run_in_thread).start()


def create_custom_ap_location_maps(working_directory, project_name, message_callback, zoomed_ap_crop_size, custom_ap_icon_size):
    wx.CallAfter(message_callback, f'Creating zoomed per AP location maps for {project_name}:{nl}'
                                   f'Custom AP icon size: {custom_ap_icon_size}{nl}'
                                   f'Zoomed AP crop size: {zoomed_ap_crop_size}{nl}')

    project_dir = Path(working_directory) / project_name

    # Load JSON data
    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    access_points_json = load_json(project_dir, 'accessPoints.json', message_callback)
    simulated_radios_json = load_json(project_dir, 'simulatedRadios.json', message_callback)

    # Process data
    floor_plans_dict = create_floor_plans_dict(floor_plans_json)
    simulated_radio_dict = create_simulated_radios_dict(simulated_radios_json)

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

    for floor in sorted(floor_plans_json['floorPlans'], key=lambda i: i['name']):

        floor_id = vector_source_check(floor, message_callback)

        # Extract floor plan and save to temp directory
        shutil.copy(project_dir / ('image-' + floor_id), temp_dir / floor_id)

        # Open the floor plan to be used for AP placement activities
        source_floor_plan_image = Image.open(temp_dir / floor_id)

        map_cropped_within_ekahau, scaling_ratio, crop_bitmap = crop_assessment(floor, source_floor_plan_image, project_dir, floor_id, blank_plan_dir)

        aps_on_this_floor = []

        for ap in sorted(access_points_json['accessPoints'], key=lambda i: i['name']):
            if ap['location']['floorPlanId'] == floor['id']:
                aps_on_this_floor.append(ap)

        if aps_on_this_floor:
            current_map_image = source_floor_plan_image.copy()

            # Generate the all_aps map
            wx.CallAfter(message_callback, f'{nl}Creating Custom AP location map for: {floor["name"]}{nl}')
            for ap in aps_on_this_floor:
                all_aps = annotate_map(current_map_image, ap, scaling_ratio, custom_ap_icon_size, simulated_radio_dict, message_callback, floor_plans_dict)

            # Save the output images
            wx.CallAfter(message_callback, f'{nl}Saving annotated floorplan: {floor["name"]}{nl}')
            all_aps.save(Path(annotated_plan_dir / floor['name']).with_suffix('.png'))


def create_custom_ap_location_maps(working_directory, project_name, message_callback, custom_ap_icon_size):

    wx.CallAfter(message_callback, f'Creating custom AP location maps for: {project_name}')
    project_dir = Path(working_directory) / project_name

    # Load JSON data
    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    access_points_json = load_json(project_dir, 'accessPoints.json', message_callback)
    simulated_radios_json = load_json(project_dir, 'simulatedRadios.json', message_callback)

    # Process data
    floor_plans_dict = create_floor_plans_dict(floor_plans_json)
    simulated_radio_dict = create_simulated_radios_dict(simulated_radios_json)

    # Create directory to hold output directories
    output_dir = working_directory / "OUTPUT"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory for Blank floor plans
    blank_plan_dir = output_dir / 'blank'
    blank_plan_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory for Annotated floorplans
    annotated_plan_dir = output_dir / 'annotated'
    annotated_plan_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory for temporary files
    temp_dir = output_dir / 'temp'
    temp_dir.mkdir(parents=True, exist_ok=True)

    for floor in floor_plans_json['floorPlans']:
        floor_id = vector_source_check(floor, message_callback)

        # Move floor plan to temp_dir
        shutil.copy(project_dir / ('image-' + floor_id), temp_dir / floor_id)

        # Open the floor plan to be used for AP placement activities
        source_floor_plan_image = Image.open(temp_dir / floor_id)

        map_cropped_within_ekahau, scaling_ratio, crop_bitmap = crop_assessment(floor, source_floor_plan_image, project_dir, floor_id, blank_plan_dir)

        aps_on_this_floor = []

        wx.CallAfter(message_callback, f'{nl}Processing floor: {floor["name"]}{nl}')

        for ap in sorted(access_points_json['accessPoints'], key=lambda i: i['name']):
            if ap['location']['floorPlanId'] == floor['id']:
                aps_on_this_floor.append(ap)

        current_map_image = source_floor_plan_image.copy()

        # Generate the all_aps map
        for ap in aps_on_this_floor:
            all_aps = annotate_map(current_map_image, ap, scaling_ratio, custom_ap_icon_size, simulated_radio_dict, message_callback, floor_plans_dict)

        # If map was cropped within Ekahau, crop the all_AP map
        if map_cropped_within_ekahau:
            all_aps = all_aps.crop(crop_bitmap)

        # Save the output images
        all_aps.save(Path(annotated_plan_dir / floor['name']).with_suffix('.png'))

    try:
        shutil.rmtree(temp_dir)
        wx.CallAfter(message_callback, f'{nl}temp directory removed')
        wx.CallAfter(message_callback, f'{nl}### PROCESS COMPLETE ###{nl}')
    except Exception as e:
        wx.CallAfter(message_callback, e)
