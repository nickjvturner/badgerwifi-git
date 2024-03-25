# SAR LY.py
from pathlib import Path

from common import load_json
from common import create_floor_plans_dict

from common import save_and_move_json
from common import re_bundle_project
from common import rename_process_completion_message as completion_message

from common import RENAMED_APS_PROJECT_APPENDIX

# Add an attribute to the module
SAR = "This is a Stand Alone Rename module"

ONE_LINER_DESCRIPTION = 'This code does not work in the visualiser yet'

sort_order_override = {
    'ADV': 'XXX',
    'HARBOUR': 'ZZZ'
}


def create_tag_keys_dict(tag_keys_json):
    """Create a dictionary of tag keys."""
    tag_keys_dict = {}
    for tagKey in tag_keys_json['tagKeys']:
        tag_keys_dict[tagKey['key']] = tagKey['id']
    return tag_keys_dict


def get_sort_value(tags_list, tag_key, tag_keys_dict):
    """Retrieves the sorting value for a given tag, applying custom sorting if specified."""
    sort_tag_id = tag_keys_dict.get(tag_key, 'Z')
    for tag in tags_list:
        if tag.get('tagKeyId') == sort_tag_id:
            return sort_order_override.get(tag.get('value'), tag.get('value', '-   ***   TagValue is empty   ***   -'))
    return 'Z'


def get_rename_value(tags_list, tag_key, tag_keys_dict):
    """Retrieves the renaming value for a given tag, avoiding custom sorting overrides."""
    rename_tag_id = tag_keys_dict.get(tag_key, 'Z')
    for tag in tags_list:
        if tag.get('tagKeyId') == rename_tag_id:
            return tag.get('value', '-   ***   TagValue is empty   ***   -')
    return 'Z'


def sort_access_points(access_points, tag_keys_dict, floor_plans_dict):
    """Sorts access points based on multiple criteria."""
    return sorted(access_points, key=lambda ap: (
        get_sort_value(ap.get('tags', []), 'UNIT', tag_keys_dict),
        get_sort_value(ap.get('tags', []), 'building-group', tag_keys_dict),
        floor_plans_dict.get(ap['location'].get('floorPlanId', 'missing_floorPlanId')),
        get_sort_value(ap.get('tags', []), 'sequence-override', tag_keys_dict),
        ap['location']['coord']['x']
    ))


def rename_aps(access_points, tag_keys_dict, floor_plans_dict, message_callback):
    """Renames access points based on sorting and specific naming conventions."""
    for i, ap in enumerate(access_points, 1):
        new_ap_name = f"{get_rename_value(ap['tags'], 'UNIT', tag_keys_dict)}-AP{i:03}"
        message_callback(f"{ap['name']} ({ap['model']}) | {floor_plans_dict.get(ap['location']['floorPlanId'], {}).get('name', 'Unknown')} | renamed to {new_ap_name}")
        ap['name'] = new_ap_name


def run(working_directory, project_name, message_callback):
    project_dir = Path(working_directory) / project_name

    # Create directory to hold output directories
    output_dir = working_directory / 'OUTPUT'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory for Blank floor plans
    renamed_aps_project_dir = output_dir / 'RENAMED APs'
    renamed_aps_project_dir.mkdir(parents=True, exist_ok=True)

    # Load JSON data
    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    access_points_json = load_json(project_dir, 'accessPoints.json', message_callback)
    tag_keys_json = load_json(project_dir, 'tagKeys.json', message_callback)

    # Process data
    floor_plans_dict = create_floor_plans_dict(floor_plans_json)
    tag_keys_dict = create_tag_keys_dict(tag_keys_json)

    # Sort Access Points
    sorted_access_points = sort_access_points(access_points_json['accessPoints'], tag_keys_dict, floor_plans_dict)

    # Rename Access Points
    rename_aps(sorted_access_points, tag_keys_dict, floor_plans_dict, message_callback)

    # Save and Move the Updated JSON
    updated_access_points_json = {'accessPoints': sorted_access_points}
    save_and_move_json(updated_access_points_json, project_dir / 'accessPoints.json')

    output_project_name = f"{project_name}{RENAMED_APS_PROJECT_APPENDIX}"
    # Re-bundle into .esx File
    re_bundle_project(project_dir, renamed_aps_project_dir, output_project_name)
    completion_message(message_callback, output_project_name)
