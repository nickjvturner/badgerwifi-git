# replacement_dict.py

import os
import wx
import json
import shutil
from pathlib import Path
import importlib.util
import base64


# Constants
VERSION = '1.2'
UNKNOWN = 'Unknown'
FIVE_GHZ_RADIO_ID = 1

nl = '\n'

ERROR = '######### ERROR #########\n\n'

SPACER = '\n\n\n'
PASS = '----\nPASS\n----\n'
FAIL = '----\nFAIL\n----\n'
CAUTION = '-------\nCAUTION\n-------\n'
HASH_BAR = '\n\n#########################\n\n'

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

# 2.4 GHz ISM band channels
ISM_channels = list(range(1, 15))

# 5 GHz UNII bands
UNII_1_channels = [36, 40, 44, 48]
UNII_2_channels = [52, 56, 60, 64]
UNII_2e_channels = list(range(100, 145, 4)) + [144]
UNII_3_channels = [149, 153, 157, 161, 165, 169, 173]

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

frequency_band_dict = {
    2400: '2.4GHz',
    5000: '5GHz',
    6000: '6GHz'
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
        'ap_name_format': [],
        'ap_name_duplication': [],
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
    name_count = {}

    for ap in access_points_json['accessPoints']:
        ap_model, external_antenna, antenna_description = model_antenna_split(ap.get('model', ''))
        ap_name = ap['name']

        # Handle duplicate AP names
        if ap_name in name_count:
            name_count[ap_name] += 1
            ap_name = f"{ap_name}_BW_DUPLICATE_AP_NAME_{name_count[ap_name]}"
            # print(f"Duplicate AP name found: {ap['name']}, renamed to: {ap_name}")
        else:
            name_count[ap_name] = 1

        custom_ap_dict[ap_name] = {
            'name': ap_name,
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


def get_tx_power_from_ies(measured_radios):
    # Extract MAC addresses and SSIDs from the dictionary
    access_points = []

    for radio in measured_radios.values():
        access_points.append((radio['mac'], radio['informationElements']))

    # Sort the access points by MAC address
    sorted_access_points = sorted(access_points)

    # Format the output string
    return '\n'.join(f"{decode_tx_power(informationElements)}" for mac, informationElements in sorted_access_points)


def decode_tx_power(ie_base64):
    # Decode the Base64-encoded IE string
    ie_bytes = base64.b64decode(ie_base64)

    index = 0
    ie_length = len(ie_bytes)
    tx_power = None  # Initialize transmit power as None

    while index < ie_length:
        # Ensure there are at least 2 bytes left for Element ID and Length
        if index + 2 > ie_length:
            break

        element_id = ie_bytes[index]
        length = ie_bytes[index + 1]
        index += 2  # Move past Element ID and Length fields

        # Ensure the data for the IE is within the bounds
        if index + length > ie_length:
            break

        element_data = ie_bytes[index:index + length]

        # Check if Element ID is 35 (TPC Report IE)
        if element_id == 35:
            if length >= 2:
                tx_power_field = element_data[0]
                link_margin = element_data[1]

               # The Transmit Power field is an unsigned integer representing dBm
                tx_power = tx_power_field  # in dBm
                print(f"Transmit Power: {tx_power} dBm")
        index += length  # Move to the next IE

    if tx_power is None:
        print("Element ID 35 (TPC Report IE) not found or does not contain transmit power.")
    return tx_power


def get_supported_rates_from_ies(measured_radios):
    # Extract MAC addresses and SSIDs from the dictionary
    access_points = []

    for radio in measured_radios.values():
        access_points.append((radio['mac'], radio['informationElements']))

    # Sort the access points by MAC address
    sorted_access_points = sorted(access_points)

    # Format the output string
    return '\n'.join(f"{decode_supported_data_rates(informationElements)}" for mac, informationElements in sorted_access_points)


def decode_supported_data_rates(ie_base64):
    # Decode the Base64-encoded IE string
    ie_bytes = base64.b64decode(ie_base64)

    index = 0
    ie_length = len(ie_bytes)
    supported_rates = []

    while index < ie_length:
        # Ensure there are at least 2 bytes left for Element ID and Length
        if index + 2 > ie_length:
            break

        element_id = ie_bytes[index]
        length = ie_bytes[index + 1]
        index += 2  # Move past Element ID and Length fields

        # Ensure the data for the IE is within the bounds
        if index + length > ie_length:
            break

        element_data = ie_bytes[index:index + length]

        # Check for Supported Rates IE (Element ID 1) and Extended Supported Rates IE (Element ID 50)
        if element_id == 1 or element_id == 50:
            for rate_byte in element_data:
                rate = (rate_byte & 0x7F) * 0.5  # Rates are in units of 0.5 Mbps
                # Check if the MSB is set; if so, it's a basic rate
                is_basic = bool(rate_byte & 0x80)
                supported_rates.append({'rate': rate, 'basic': is_basic})
        index += length  # Move to the next IE

    # Remove duplicates and sort rates in ascending order
    unique_rates = {}
    for rate_info in supported_rates:
        rate = rate_info['rate']
        is_basic = rate_info['basic']
        # If the rate is already in the dict, mark it as basic if either occurrence is basic
        if rate in unique_rates:
            unique_rates[rate] = unique_rates[rate] or is_basic
        else:
            unique_rates[rate] = is_basic

    # Sort the rates
    sorted_rates = sorted(unique_rates.items())

    # Create a list of rate strings
    rates_display = []
    for rate, is_basic in sorted_rates:
        rate_str = f"{int(rate)}"
        if is_basic:
            rate_str += " (B)"
        rates_display.append(rate_str)

    # Join the rates into a single string
    rates_output = ", ".join(rates_display)

    # Output the supported data rates
    print(rates_output)

    return rates_output


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


def get_channel_from_ies(measured_radios):
    # Extract MAC addresses and SSIDs from the dictionary
    access_points = []

    for radio in measured_radios.values():
        access_points.append((radio['mac'], radio['informationElements']))

    # Sort the access points by MAC address
    sorted_access_points = sorted(access_points)

    # Format the output string
    return '\n'.join(f"{decode_channel(informationElements)}" for mac, informationElements in sorted_access_points)


def decode_channel(ie_base64):
    # Decode the Base64-encoded IE string
    ie_bytes = base64.b64decode(ie_base64)

    index = 0
    ie_length = len(ie_bytes)
    channel = None  # Initialize channel as None

    while index < ie_length:
        # Ensure there are at least 2 bytes left for Element ID and Length
        if index + 2 > ie_length:
            break

        element_id = ie_bytes[index]
        length = ie_bytes[index + 1]
        index += 2  # Move past Element ID and Length fields

        # Ensure the data for the IE is within the bounds
        if index + length > ie_length:
            break

        element_data = ie_bytes[index:index + length]

        # Check if Element ID is 3 (DS Parameter Set)
        if element_id == 3:
            if length >= 1:
                channel = element_data[0]
                print(f"Channel: {channel}")
                # Optionally, you can return here if only one occurrence is expected
                # return channel
        index += length  # Move to the next IE

    if channel is None:
        print("Element ID 3 (DS Parameter Set) not found or does not contain channel information.")
    return channel


def get_wifi_band_from_ie_channel(measured_radios):
    # Extract MAC addresses and SSIDs from the dictionary
    access_points = []

    for radio in measured_radios.values():
        access_points.append((radio['mac'], radio['informationElements']))

    # Sort the access points by MAC address
    sorted_access_points = sorted(access_points)

    # Format the output string
    return '\n'.join(f"{lookup_wifi_band(decode_channel(informationElements))}" for mac, informationElements in sorted_access_points)


def lookup_wifi_band(channel):
    """
    Returns the Wi-Fi band for a given channel number.

    Parameters:
    - channel (int): The Wi-Fi channel number.

    Returns:
    - str: The band in which the channel exists.
    """

    if channel in ISM_channels:
        return 'ISM'
    elif channel in UNII_1_channels:
        return 'UNII-1'
    elif channel in UNII_2_channels:
        return 'UNII-2'
    elif channel in UNII_2e_channels:
        return 'UNII-2e'
    elif channel in UNII_3_channels:
        return 'UNII-3'
    else:
        return 'Unknown or unsupported channel'


def antenna_name_cleanup(antenna_name):
    """
        Removes all occurrences of the band_references from the antenna_name.

        Returns:
        str: The modified antenna_name with all substrings removed.
        """
    for ref in antenna_band_references:
        antenna_name = antenna_name.replace(ref, "")

    return antenna_name
