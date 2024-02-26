# rename_aps_LY.py

import json
from pathlib import Path
import shutil

from root_common import load_json, create_floor_plans_dict

def create_tag_keys_dict(tagKeysJSON):
    """Create a dictionary of tag keys."""
    tagKeysDict = {}
    for tagKey in tagKeysJSON['tagKeys']:
        tagKeysDict[tagKey['key']] = tagKey['id']
    return tagKeysDict

def sort_tag_value_getter(tagsList, sortTagKey, tagKeysDict):
    """Retrieve the value of a specific tag for sorting purposes."""
    undefined_TagValue = '-   ***   TagValue is empty   ***   -'
    missing_TagKey = 'Z'
    sortTagUniqueId = tagKeysDict.get(sortTagKey)
    if sortTagUniqueId is None:
        return missing_TagKey
    for value in tagsList:
        if value.get('tagKeyId') == sortTagUniqueId:
            tagValue = value.get('value')
            if tagValue is None:
                return undefined_TagValue
            return tagValue
    return missing_TagKey

def sort_access_points(accessPoints, tagKeysDict, floorPlansDict):
    """Sort access points based on various criteria."""
    return sorted(accessPoints,
                  key=lambda ap: (
                      sort_tag_value_getter(ap.get('tags', []), 'UNIT', tagKeysDict),
                      sort_tag_value_getter(ap.get('tags', []), 'building-group', tagKeysDict),
                      floorPlansDict.get(ap['location'].get('floorPlanId', 'missing_floorPlanId')),
                      sort_tag_value_getter(ap.get('tags', []), 'sequence-override', tagKeysDict),
                      ap['location']['coord']['x']
                  ))

def rename_access_points(accessPoints, tagKeysDict, floorPlansDict, message_callback):
    """Rename access points based on sorting and specific naming conventions."""
    apSeqNum = 1
    for ap in accessPoints:
        new_AP_name = f"{sort_tag_value_getter(ap['tags'], 'UNIT', tagKeysDict)}-AP{apSeqNum:03}"

        message_callback(
            f"[[ {ap['name']} [{ap['model']}]] from: {floorPlansDict.get(ap['location']['floorPlanId'])} ] renamed to {new_AP_name}")

        ap['name'] = new_AP_name
        apSeqNum += 1

def save_and_move_json(data, filePath):
    """Save the updated access points to a JSON file."""
    with open(filePath, "w") as outfile:
        json.dump(data, outfile, indent=4)

def re_bundle_project(projectDir, outputName):
    """Re-bundle the project directory into an .esx file."""
    output_esx_path = projectDir.parent / outputName
    shutil.make_archive(str(output_esx_path), 'zip', str(projectDir))
    output_zip_path = str(output_esx_path) + '.zip'
    output_esx_path = str(output_esx_path) + '.esx'
    shutil.move(output_zip_path, output_esx_path)

def rename_aps(working_directory, project_name, message_callback):
    project_dir = Path(working_directory) / project_name

    # Load JSON data
    floorPlansJSON = load_json(project_dir, 'floorPlans.json')
    accessPointsJSON = load_json(project_dir, 'accessPoints.json')
    tagKeysJSON = load_json(project_dir, 'tagKeys.json')

    # Process data
    floorPlansDict = create_floor_plans_dict(floorPlansJSON)
    tagKeysDict = create_tag_keys_dict(tagKeysJSON)

    # Sort Access Points
    sortedAccessPoints = sort_access_points(accessPointsJSON['accessPoints'], tagKeysDict, floorPlansDict)

    # Rename Access Points
    rename_access_points(sortedAccessPoints, tagKeysDict, floorPlansDict, message_callback)

    # Save and Move the Updated JSON
    updatedAccessPointsJSON = {'accessPoints': sortedAccessPoints}
    save_and_move_json(updatedAccessPointsJSON, project_dir / 'accessPoints.json')

    # Re-bundle into .esx File
    re_bundle_project(project_dir, f"{project_name}_re-zip")

    message_callback(f"\nProcess complete\n{project_name}_re-zip re-bundled into .esx file")
