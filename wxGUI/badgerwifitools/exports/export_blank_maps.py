# blank_map_exporter.py

import shutil
from pathlib import Path
from PIL import Image

from common import load_json
from common import create_floor_plans_dict

# Variables
nl = '\n'


def vector_source_check(floor):
    return floor.get('bitmapImageId', floor['imageId'])

def export_floor_plan(source, destination, crop_bitmap=None):
    with Image.open(source) as img:
        if crop_bitmap:
            img = img.crop(crop_bitmap)
        img.save(destination)


def export_blank_maps(working_directory, project_name, message_callback):
    project_dir = Path(working_directory) / project_name
    output_dir = working_directory / "OUTPUT" / 'blank'
    output_dir.mkdir(parents=True, exist_ok=True)

    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)

    for floor in floor_plans_json['floorPlans']:
        floor_id = vector_source_check(floor)
        source_path = project_dir / f'image-{floor_id}'
        dest_path = output_dir / f"{floor['name']}.png"

        if 'cropMinX' in floor and floor['cropMinX'] != 0.0:
            crop_bitmap = (
                floor['cropMinX'], floor['cropMinY'],
                floor['cropMaxX'], floor['cropMaxY']
            )
            export_floor_plan(source_path, dest_path, crop_bitmap=crop_bitmap)
        else:
            shutil.copy(source_path, dest_path)

        message_callback(f'Exported blank map for {floor["name"]}')

if __name__ == '__main__':
    working_directory = '/path/to/working/directory'
    project_name = 'ProjectName'
    message_callback = print  # Using print function as a simple callback for messages
    export_blank_maps(working_directory, project_name, message_callback)


# def vector_source_check(floor):
#     if 'bitmapImageId' in floor:
#         print(f'bitmapImageId detected, floor plan source probably vector')
#         return floor['bitmapImageId']
#
#     else:
#         return floor['imageId']
#
#
# def export_blank_maps(working_directory, project_name, message_callback):
#
#     message_callback(f'Exporting plain map image files from: {project_name}\n')
#     project_dir = Path(working_directory) / project_name
#
#     def crop_assessment():
#         # Check if the floorplan has been cropped within Ekahau?
#         crop_bitmap = (floor['cropMinX'], floor['cropMinY'], floor['cropMaxX'], floor['cropMaxY'])
#
#         if crop_bitmap[0] != 0.0 or crop_bitmap[1] != 0.0:
#
#             # Calculate scaling ratio
#             scaling_ratio = all_aps.width / floor['width']
#
#             # Calculate x,y coordinates of the crop within Ekahau
#             crop_bitmap = (crop_bitmap[0] * scaling_ratio,
#                            crop_bitmap[1] * scaling_ratio,
#                            crop_bitmap[2] * scaling_ratio,
#                            crop_bitmap[3] * scaling_ratio)
#
#             # set boolean value
#             map_cropped_within_ekahau = True
#
#             # save a blank copy of the cropped floor plan
#             cropped_blank_map = source_floor_plan_image.copy()
#             cropped_blank_map = cropped_blank_map.crop(crop_bitmap)
#             cropped_blank_map.save(Path(blank_plan_dir / floor['name']).with_suffix('.png'))
#
#             return map_cropped_within_ekahau, scaling_ratio, crop_bitmap
#
#         else:
#             # There is no crop
#             scaling_ratio = 1
#
#             # set boolean value
#             map_cropped_within_ekahau = False
#
#             # save a blank copy of the floorplan
#             shutil.copy(project_dir / ('image-' + floor_id),
#                         Path(blank_plan_dir / floor['name']).with_suffix('.png'))
#
#             return map_cropped_within_ekahau, scaling_ratio, None
#
#     # Load JSON data
#     floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
#     access_points_json = load_json(project_dir, 'accessPoints.json', message_callback)
#     simulated_radios_json = load_json(project_dir, 'simulatedRadios.json', message_callback)
#
#     # Process data
#     floor_plans_dict = create_floor_plans_dict(floor_plans_json)
#     simulated_radio_dict = create_simulated_radios_dict(simulated_radios_json)
#
#     # Create directory to hold output directories
#     output_dir = working_directory / "OUTPUT"
#     output_dir.mkdir(parents=True, exist_ok=True)
#
#     # Create subdirectory for Blank floor plans
#     blank_plan_dir = output_dir / 'blank'
#     blank_plan_dir.mkdir(parents=True, exist_ok=True)
#
#     # Create subdirectory for temporary files
#     temp_dir = output_dir / 'temp'
#     temp_dir.mkdir(parents=True, exist_ok=True)
#
#     for floor in floor_plans_json['floorPlans']:
#
#         floor_id = vector_source_check(floor)
#
#         # Extract floor plan
#         shutil.copy(project_dir / ('image-' + floor_id), temp_dir / floor_id)
#
#         # Open the floor plan to be used for AP placement activities
#         source_floor_plan_image = Image.open(temp_dir / floor_id)
#
#         aps_on_this_floor = []
#
#         for ap in sorted(access_points_json['accessPoints'], key=lambda i: i['name']):
#             # print(ap)
#             # print(ap['location']['floorPlanId'])
#             if ap['location']['floorPlanId'] == floor['id']:
#                 aps_on_this_floor.append(ap)
#
#         current_map_image = source_floor_plan_image.copy()
#
#     try:
#         shutil.rmtree(temp_dir)
#         print(f'Temporary project contents directory removed{nl}')
#     except Exception as e:
#         print(e)
