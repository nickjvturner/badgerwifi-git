# create_custom_ap_location_maps.py

import shutil
from pathlib import Path
from PIL import Image
import threading
import wx

from common import nl
from common import load_json
from common import create_floor_plans_dict
from common import create_simulated_radios_dict

from map_creator.map_creator_comon import vector_source_check
from map_creator.map_creator_comon import crop_assessment
from map_creator.map_creator_comon import annotate_map
from map_creator.map_creator_comon import crop_map

from map_creator.map_creator_comon import OPACITY

CUSTOM_AP_ICON_SIZE_ADJUSTER = 4.87


def create_zoomed_ap_location_maps_threaded(working_directory, project_name, message_callback, zoomed_ap_crop_size, custom_ap_icon_size, stop_event):
    # Wrapper function to run insert_images in a separate thread
    def run_in_thread():
        create_zoomed_ap_location_maps(working_directory, project_name, message_callback, zoomed_ap_crop_size, custom_ap_icon_size, stop_event)
    # Start the long-running task in a separate thread
    threading.Thread(target=run_in_thread).start()


def create_zoomed_ap_location_maps(working_directory, project_name, message_callback, zoomed_ap_crop_size, custom_ap_icon_size, stop_event):
    wx.CallAfter(message_callback, f'Creating zoomed per AP location maps for {project_name}:{nl}'
                                   f'Custom AP icon size: {custom_ap_icon_size}{nl}'
                                   f'Zoomed AP crop size: {zoomed_ap_crop_size}{nl}')

    custom_ap_icon_size = int(custom_ap_icon_size * CUSTOM_AP_ICON_SIZE_ADJUSTER)

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
    zoom_faded_dir = output_dir / 'zoomed AP location maps'
    zoom_faded_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory for Custom AP Location maps
    custom_ap_location_maps = output_dir / 'custom AP location maps'
    custom_ap_location_maps.mkdir(parents=True, exist_ok=True)

    # Create subdirectory for temporary files
    temp_dir = output_dir / 'temp'
    temp_dir.mkdir(parents=True, exist_ok=True)

    for floor in sorted(floor_plans_json['floorPlans'], key=lambda i: i['name']):
        if stop_event.is_set():
            wx.CallAfter(message_callback, f'{nl}### PROCESS ABORTED ###')
            return

        floor_id = vector_source_check(floor, message_callback)

        # Extract floor plan and save to temp directory
        shutil.copy(project_dir / ('image-' + floor_id), temp_dir / floor_id)

        # Open the floor plan to be used for AP placement activities
        source_floor_plan_image = Image.open(temp_dir / floor_id)

        map_cropped_within_ekahau, scaling_ratio, crop_bitmap = crop_assessment(floor, source_floor_plan_image, project_dir, floor_id, blank_plan_dir)

        aps_on_this_floor = []

        for ap in sorted(access_points_json['accessPoints'], key=lambda i: i['name']):
            if stop_event.is_set():
                wx.CallAfter(message_callback, f'{nl}### PROCESS ABORTED ###')
                return

            if ap['location']['floorPlanId'] == floor['id']:
                aps_on_this_floor.append(ap)

        if aps_on_this_floor:
            if stop_event.is_set():
                wx.CallAfter(message_callback, f'{nl}### PROCESS ABORTED ###')
                return

            current_map_image = source_floor_plan_image.copy()

            # Generate the all_aps map
            wx.CallAfter(message_callback, f'{nl}Creating Custom AP location map for: {floor["name"]}{nl}')
            for ap in aps_on_this_floor:
                if stop_event.is_set():
                    wx.CallAfter(message_callback, f'{nl}### PROCESS ABORTED ###')
                    return
                all_aps = annotate_map(current_map_image, ap, scaling_ratio, custom_ap_icon_size, simulated_radio_dict, message_callback, floor_plans_dict)

            # Save the output images
            wx.CallAfter(message_callback, f'{nl}Saving annotated floor plan: {floor["name"]}{nl}')
            all_aps.save(Path(custom_ap_location_maps / floor['name']).with_suffix('.png'))

            # Zoom faded AP map generation
            wx.CallAfter(message_callback, f'{nl}Creating zoomed per AP images for: {floor["name"]}{nl}')
            all_aps_faded = all_aps.copy().convert('RGBA')
            faded_ap_background_map_image = source_floor_plan_image.convert('RGBA')
            all_aps_faded = Image.alpha_composite(faded_ap_background_map_image, Image.blend(faded_ap_background_map_image, all_aps_faded, OPACITY))

            for ap in aps_on_this_floor:
                if stop_event.is_set():
                    wx.CallAfter(message_callback, f'{nl}### PROCESS ABORTED ###')
                    return

                per_ap_map_image = annotate_map(all_aps_faded.copy(), ap, scaling_ratio, custom_ap_icon_size, simulated_radio_dict, message_callback, floor_plans_dict)

                cropped_per_ap_map_image = crop_map(per_ap_map_image, ap, scaling_ratio, zoomed_ap_crop_size)

                # Save the cropped image with a new filename
                cropped_per_ap_map_image.save(Path(zoom_faded_dir / (ap['name'] + '-zoomed')).with_suffix('.png'))

            # If map was cropped within Ekahau, crop the all_AP map
            if map_cropped_within_ekahau:
                all_aps = all_aps.crop(crop_bitmap)

        else:
            wx.CallAfter(message_callback, f'{nl}No APs found on floor: {floor["name"]}{nl}')

    try:
        shutil.rmtree(temp_dir)
        wx.CallAfter(message_callback, f'{nl}### Process Complete ###{nl}')
    except Exception as e:
        print(e)
