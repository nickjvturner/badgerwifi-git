# blank_map_exporter.py

import shutil
from pathlib import Path

import wx
from PIL import Image

from common import load_json
from map_creator.map_creator_comon import vector_source_check

# Variables
nl = '\n'


def export_floor_plan(source, destination, crop_bitmap=None):
    with Image.open(source) as img:
        if crop_bitmap:
            img = img.crop(crop_bitmap)
        img.save(destination)


def extract_blank_maps(working_directory, project_name, message_callback):
    project_dir = Path(working_directory) / project_name
    output_dir = working_directory / 'OUTPUT' / 'blank'
    output_dir.mkdir(parents=True, exist_ok=True)

    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)

    for floor in floor_plans_json['floorPlans']:
        floor_id = vector_source_check(floor, message_callback)
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

        wx.CallAfter(message_callback, f"{nl}Exported blank map for {floor['name']} to:{nl}{dest_path}{nl}")
    wx.CallAfter(message_callback, f"{nl}### PROCESS COMPLETE ###")
