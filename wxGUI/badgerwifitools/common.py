# replacement_dict.py

import os
import wx
import json
import shutil
from pathlib import Path

# Constants
VERSION = '1.2'
UNKNOWN = 'Unknown'
FIVE_GHZ_RADIO_ID = 1

nl = '\n'

ESX_EXTENSION = '.esx'
DOCX_EXTENSION = '.docx'
CONFIGURATION_DIR = 'configuration'
PROJECT_PROFILES_DIR = 'project_profiles'
RENAME_APS_DIR = 'rename_aps'

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
    '#00FFCE': 'mint',
    'None': 'default'
}

# Define your custom model sort order here
model_sort_order = {
    'AP-655': '1',
    'AP-514': '2'
}

acceptable_antenna_tilt_angles = (0, -10, -20, -30, -40, -45, -50, -60, -70, -80, -90)


def load_json(project_dir, filename, message_callback):
    """Load JSON data from a file."""
    try:
        with open(project_dir / filename) as json_file:
            return json.load(json_file)
    except IOError as e:
        print(f'{filename} not found, the project probably does not contain this data type.')
        # print(f"Non-critical error{nl}{filename}: {e}")
        return None


def create_floor_plans_dict(floor_plans_json):
    """Create a dictionary of pertinent floor plan detail."""
    return {
        floor['id']: {
            'name': floor['name'],
            'height': floor['height']
        } for floor in floor_plans_json['floorPlans']
    }


def create_notes_dict(notes_json):
    """Create a dictionary of notes."""
    if not notes_json:
        # If notesJSON contains no notes, return None
        return None

    notes_dict = {}
    for note in notes_json['notes']:
        notes_dict[note['id']] = note
    return notes_dict


def note_text_processor(note_ids, notes_dict):
    notes_text = []
    if note_ids:
        for noteId in note_ids:
            # Attempt to retrieve the note by ID and its 'text' field
            note = notes_dict.get(noteId, {})
            text = note.get('text', None)  # Use None as the default

            # Append the text to notes_text only if it exists and is not empty
            if text:  # This condition is True if text is not None and not an empty string
                notes_text.append(text)

        return '\n'.join(notes_text)  # Join all non-empty note texts into a single string
    return ''


def create_tag_keys_dict(tag_keys_json):
    """Create a dictionary of tag keys."""
    # Initialize an empty dictionary
    tag_keys_dict = {}

    # Check if tag_keys_json exists and has the expected structure
    if tag_keys_json is not None and isinstance(tag_keys_json, dict) and 'tagKeys' in tag_keys_json:
        try:
            # Iterate through each item in 'tagKeys'
            for tagKey in tag_keys_json['tagKeys']:
                # Add the id and key to the tag_keys_dict
                tag_keys_dict[tagKey.get('id')] = tagKey.get('key')
        except (TypeError, KeyError) as e:
            # Handle potential exceptions that might occur with incorrect input format
            print(f"Non-critical error: {e}")
            return None
    else:
        return None

    return tag_keys_dict


def create_simulated_radios_dict(simulated_radios_json):
    simulated_radio_dict = {}  # Initialize an empty dictionary

    # Loop through each radio inside simulatedRadiosJSON['simulatedRadios']
    for radio in simulated_radios_json['simulatedRadios']:
        # Check if the top-level key exists, if not, create it
        if radio['accessPointId'] not in simulated_radio_dict:
            simulated_radio_dict[radio['accessPointId']] = {}

        # Assign the radio object to the nested key
        simulated_radio_dict[radio['accessPointId']][radio['accessPointIndex']] = radio

    return simulated_radio_dict


def model_antenna_split(string):
    """Split external antenna information."""
    # Split the input string by the '+' sign
    segments = string.split('+')

    # Strip leading/trailing spaces from each part
    segments = [segment.strip() for segment in segments]

    # Extract the AP model, which is always present
    ap_model = segments[0]

    # Extract the external antenna if present
    if len(segments) > 1:
        external_antenna = segments[1]
        antenna_description = 'External'
    else:
        external_antenna = None
        antenna_description = 'Integrated'

    return ap_model, external_antenna, antenna_description


def file_or_dir_exists(path):
    """
    Check if a file or directory exists at the given path.

    Parameters:
    - path (str or Path): The path to the file or directory.

    Returns:
    - bool: True if the file or directory exists, False otherwise.
    """
    target_path = Path(path)
    return target_path.exists()


def offender_constructor(required_tag_keys, optional_tag_keys):
    offenders = {
        'color': [],
        'antennaHeight': [],
        'bluetooth': [],
        'missing_required_tags': {},
        'missing_optional_tags': {},
        'antennaTilt': [],
        'antennaMounting_and_antennaTilt_mismatch': [],

    }

    for tagKey in required_tag_keys:
        offenders['missing_required_tags'][tagKey] = []

    for tagKey in optional_tag_keys:
        offenders['missing_required_tags'][tagKey] = []

    return offenders


def save_and_move_json(data, file_path):
    """Save the updated access points to a JSON file."""
    with open(file_path, "w") as outfile:
        json.dump(data, outfile, indent=4)


def re_bundle_project(project_dir, output_name):
    """Re-bundle the project directory into an .esx file."""
    output_esx_path = project_dir.parent / output_name
    shutil.make_archive(str(output_esx_path), 'zip', str(project_dir))
    output_zip_path = str(output_esx_path) + '.zip'
    output_esx_path = str(output_esx_path) + '.esx'
    shutil.move(output_zip_path, output_esx_path)


def create_custom_ap_dict(access_points_json, floor_plans_dict, simulated_radio_dict):
    custom_ap_dict = {}
    for ap in access_points_json['accessPoints']:
        ap_model, external_antenna, antenna_description = model_antenna_split(ap.get('model', ''))

        custom_ap_dict[ap['name']] = {
            'name': ap['name'],
            'color': ap.get('color', 'none'),
            'model': ap_model,
            'antenna': external_antenna,
            'floor': floor_plans_dict.get(ap['location']['floorPlanId']).get('name'),
            'antennaTilt': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaTilt', ''),
            'antennaMounting': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaMounting', ''),
            'antennaHeight': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaHeight', 0),
            'radios': simulated_radio_dict.get(ap['id'], {}),
            'remarks': '',
            'ap bracket': '',
            'antenna bracket': '',
            'tags': {}
            }

    return custom_ap_dict


def rename_aps(sorted_ap_list, message_callback, floor_plans_dict):
    ap_sequence_number = 1

    for ap in sorted_ap_list:
        # Define new AP naming scheme
        new_ap_name = f'AP-{ap_sequence_number:03}'

        wx.CallAfter(message_callback, f"{ap['name']} ][ {model_antenna_split(ap['model'])[0]} from: {floor_plans_dict.get(ap['location']['floorPlanId']).get('name')} ][ renamed: {new_ap_name}")

        ap['name'] = new_ap_name
        ap_sequence_number += 1

    return sorted_ap_list


def rename_process_completion_message(message_callback, project_name):
    wx.CallAfter(message_callback, f"{nl}Modified accessPoints.json re-bundled into .esx file{nl}{project_name}_re-zip.esx within working directory{nl}{nl}### PROCESS COMPLETE ###")


def discover_available_scripts(directory):
    """
    General-purpose function to discover available Python script files in a specified directory.
    Excludes files starting with underscores or 'common'.
    """
    script_dir = Path(__file__).resolve().parent / directory
    available_scripts = []
    for filename in os.listdir(script_dir):
        if filename.endswith(".py") and not filename.startswith(("_", "common")):
            available_scripts.append(filename[:-3])
    return sorted(available_scripts)
