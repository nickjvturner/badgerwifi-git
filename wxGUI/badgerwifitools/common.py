# replacement_dict.py

import os
import wx
import json
import shutil
from pathlib import Path
import importlib.util


# Constants
VERSION = '1.2'
UNKNOWN = 'Unknown'
FIVE_GHZ_RADIO_ID = 1

nl = '\n'

ESX_EXTENSION = '.esx'
DOCX_EXTENSION = '.docx'
CONFIGURATION_DIR = 'configuration'
PROJECT_PROFILES_DIR = 'project_profiles'
RENAME_APS_DIR = 'rename_aps/rename_scripts'
RENAMED_APS_PROJECT_APPENDIX = '__APs_RENAMED'
BOUNDARY_SEPARATION_WIDGET = 'BOUNDARY_SEPARATOR'
PROJECT_DETAIL_DIR = 'project_detail'
ADMIN_ACTIONS_DIR = 'admin/actions'
DIR_STRUCTURE_PROFILES_DIR = 'admin/dir_structure_profiles'
OVERSIZE_MAP_LIMIT = 8000

WHIMSY_WELCOME_MESSAGES = [
    'Welcome to BadgerWiFi Tools',
    "Fancy seeing you here!",
    "If you're reading this, you're probably a WiFi professional",
    "Let's get started!",
    ]

CALL_TO_DONATE_MESSAGE = f"{'#' * 30}{nl}{nl}If you are finding this tool useful, please consider supporting the developer!{nl}Please consider buying @nickjvturner a coffee{nl}{nl}https://ko-fi.com/badgerwifitools{nl}{nl}{'#' * 30}"

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

range_two = (2400, 2500)
range_five = (5000, 5900)
range_six = (5901, 7200)

wifi_channel_dict = {
    2412: 1,
    2417: 2,
    2422: 3,
    2427: 4,
    2432: 5,
    2437: 6,
    2442: 7,
    2447: 8,
    2452: 9,
    2457: 10,
    2462: 11,
    2467: 12,
    2472: 13,
    2484: 14,

    5180: 36,
    5200: 40,
    5220: 44,
    5240: 48,
    5260: 52,
    5280: 56,
    5300: 60,
    5320: 64,
    5500: 100,
    5520: 104,
    5540: 108,
    5560: 112,
    5580: 116,
    5600: 120,
    5620: 124,
    5640: 128,
    5660: 132,
    5680: 136,
    5700: 140,
    5720: 144,
    5745: 149,
    5765: 153,
    5785: 157,
    5805: 161,
    5825: 165,

    5955: 1,
    5975: 5,
    5995: 9,
    6015: 13,
    6035: 17,
    6055: 21,
    6075: 25,
    6095: 29,
    6115: 33,
    6135: 37,
    6155: 41,
    6175: 45,
    6195: 49,
    6215: 53,
    6235: 57,
    6255: 61,
    6275: 65,
    6295: 69,
    6315: 73,
    6335: 77,
    6355: 81,
    6375: 85,
    6395: 89,
    6415: 93,
    6435: 97,
    6455: 101,
    6475: 105,
    6495: 109,
    6515: 113,
    6535: 117,
    6555: 121,
    6575: 125,
    6595: 129,
    6615: 133,
    6635: 137,
    6655: 141,
    6675: 145,
    6695: 149,
    6715: 153,
    6735: 157,
    6755: 161,
    6775: 165,
    6795: 169,
    6815: 173,
    6835: 177,
    6855: 181,
    6875: 185,
    6895: 189,
    6915: 193,
    6935: 197,
    6955: 201,
    6975: 205,
    6995: 209,
    7015: 213,
    7035: 217,
    7055: 221,
    7075: 225,
    7095: 229
}


antenna_band_references = (' BLE', ' 2.4GHz', ' 5GHz', ' 6GHz')


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


def create_antenna_types_dict(antenna_types_json):
    antenna_types_dict = {}  # Initialize an empty dictionary

    # Loop through each antenna inside antennaTypesJSON['antennaTypes']
    for antenna in antenna_types_json['antennaTypes']:
        # Check if the top-level key exists, if not, create it
        if antenna['id'] not in antenna_types_dict:
            antenna_types_dict[antenna['id']] = {}

        # Assign the antenna object to the nested key
        antenna_types_dict[antenna['id']] = antenna

    return antenna_types_dict


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


def re_bundle_project(project_dir, output_dir, output_name):
    """Re-bundle the project directory into an .esx file."""
    output_esx_path = output_dir / output_name
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


def rename_process_completion_message(message_callback, output_project_name):
    wx.CallAfter(message_callback, f"{nl}Modified accessPoints.json re-bundled into {output_project_name}.esx{nl}File saved within the 'OUTPUT' directory{nl}{nl}### PROCESS COMPLETE ###")


def discover_available_scripts(directory, ignore_files=("_", "common")):
    """
    General-purpose function to discover available Python script files in a specified directory.
    Excludes files starting with underscores or 'common'.
    """
    script_dir = Path(__file__).resolve().parent / directory
    available_scripts = []
    for filename in os.listdir(script_dir):
        if filename.endswith(".py") and not filename.startswith(ignore_files):
            available_scripts.append(filename[:-3])
    return sorted(available_scripts)


def create_access_point_measurements_dict(access_point_measurements_json):
    access_point_measurements_dict = {}  # Initialize an empty dictionary

    # Loop through each radio inside access_point_measurements_json['accessPointMeasurements']
    for ap in access_point_measurements_json['accessPointMeasurements']:
        # Check if the top-level key exists, if not, create it
        if ap['id'] not in access_point_measurements_dict:
            access_point_measurements_dict[ap['id']] = {}

        # Assign the radio object to the nested key
        access_point_measurements_dict[ap['id']] = ap

    return access_point_measurements_dict


def create_measured_radios_dict(measured_radios_json, access_point_measurements_dict):
    measured_radios_dict = {}  # Initialize an empty dictionary

    for radio in measured_radios_json['measuredRadios']:
        # Check if the top-level key exists, if not, create it
        if radio['accessPointId'] not in measured_radios_dict:
            measured_radios_dict[radio['accessPointId']] = {}

        for measurement_id in radio.get('accessPointMeasurementIds', []):
            access_point_measurement = access_point_measurements_dict.get(measurement_id)
            if access_point_measurement:
                lowest_center_frequency = access_point_measurement.get('channelByCenterFrequencyDefinedNarrowChannels')[0]
                mac = access_point_measurement.get('mac')
                access_point_id = radio['accessPointId']

                if range_two[0] <= lowest_center_frequency <= range_two[1]:
                    if 'two' not in measured_radios_dict[access_point_id]:
                        measured_radios_dict[access_point_id]['two'] = {}
                    measured_radios_dict[access_point_id]['two'][mac] = access_point_measurement

                elif range_five[0] <= lowest_center_frequency <= range_five[1]:
                    if 'five' not in measured_radios_dict[access_point_id]:
                        measured_radios_dict[access_point_id]['five'] = {}
                    measured_radios_dict[access_point_id]['five'][mac] = access_point_measurement

                elif range_six[0] <= lowest_center_frequency <= range_six[1]:
                    if 'six' not in measured_radios_dict[access_point_id]:
                        measured_radios_dict[access_point_id]['six'] = {}
                    measured_radios_dict[access_point_id]['six'][mac] = access_point_measurement

    return measured_radios_dict


def import_module_from_path(module_name, path_to_module):
    spec = importlib.util.spec_from_file_location(module_name, path_to_module)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_ssid_and_mac(measured_radios):
    # Extract MAC addresses and SSIDs from the dictionary
    access_points = []

    for radio in measured_radios.values():
        access_points.append((radio['mac'], radio['ssid']))

    # Sort the access points by MAC address
    sorted_access_points = sorted(access_points)

    # Format the output string
    return '\n'.join(f"{ssid} ({mac})" for mac, ssid in sorted_access_points)


def get_security_and_technologies(measured_radios):
    # Extract MAC addresses and SSIDs from the dictionary
    access_points = []

    for radio in measured_radios.values():
        access_points.append((radio['mac'], radio['security'], radio['technologies']))

    # Sort the access points by MAC address
    sorted_access_points = sorted(access_points)

    # Format the output string
    return '\n'.join(f"{security} {technologies}" for mac, security, technologies in sorted_access_points)


def extract_frequency_channel_and_width(data, band):
    channels_and_widths = []
    if band in data:
        access_points = data[band]
        first_ap_data = next(iter(access_points.values()))
        frequencies = first_ap_data['channelByCenterFrequencyDefinedNarrowChannels']
        first_frequency = frequencies[0]
        width = 20 * len(frequencies)
        channels_and_widths.append((first_frequency, frequencies, width))

    else:
        channels_and_widths.append(('', '', ''))

    return tuple(channels_and_widths)


def antenna_name_cleanup(antenna_name):
    """
        Removes all occurrences of the band_references from the antenna_name.

        Returns:
        str: The modified antenna_name with all substrings removed.
        """
    for ref in antenna_band_references:
        antenna_name = antenna_name.replace(ref, "")

    return antenna_name
