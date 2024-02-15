# common.py

import json

# Constants
UNKNOWN = 'Unknown'
VERSION = '1.2'
FIVE_GHZ = 'FIVE'

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


def load_json(project_dir, filename):
    """Load JSON data from a file."""
    try:
        with open(project_dir / filename) as json_file:
            return json.load(json_file)
    except IOError as e:
        print(f"Error loading {filename}: {e}")
        return None


def create_floor_plans_dict(floorPlansJSON):
    """Create a dictionary of floor plans."""
    floorPlansDict = {}
    for floor in floorPlansJSON['floorPlans']:
        floorPlansDict[floor['id']] = floor['name']
    return floorPlansDict


def create_notes_dict(notesJSON):
    """Create a dictionary of notes."""
    notesDict = {}
    for note in notesJSON['notes']:
        notesDict[note['id']] = note
    return notesDict

def note_text_processor(noteIds, notesDict):
    notes_text = []
    if noteIds:
        for noteId in noteIds:
            notes_text.append(notesDict.get(noteId).get(('text'), ''))
        return '\n'.join(notes_text)  # Join all note texts into a single string
    return ''


def create_tag_keys_dict(tagKeysJSON):
    """Create a dictionary of tag keys."""
    tagKeysDict = {}
    for tagKey in tagKeysJSON['tagKeys']:
        tagKeysDict[tagKey['id']] = tagKey['key']
    return tagKeysDict


def create_simulated_radios_dict(simulatedRadiosJSON):
    simulatedRadioDict = {}  # Initialize an empty dictionary

    # Loop through each radio inside simulatedRadiosJSON['simulatedRadios']
    for radio in simulatedRadiosJSON['simulatedRadios']:
        # Create mini dictionary to establish frequency band of each radio object
        miniFrequencyBandDict = {} # Initialize an empty dictionary

        # Populate mini dictionary with antennaTypeId to frequencyBand pairing
        for antenna in radio['defaultAntennas']:
            miniFrequencyBandDict[antenna['antennaTypeId']] = antenna['frequencyBand']

        # Populate simulatedRadioDict with nested objects keyed by accessPointId, frequencyBand
        if radio['accessPointId'] not in simulatedRadioDict:
            simulatedRadioDict[radio['accessPointId']] = {}
        simulatedRadioDict[radio['accessPointId']][miniFrequencyBandDict[radio['antennaTypeId']]] = radio

    return simulatedRadioDict


def external_ant_split(s):
    """Split external antenna information."""
    return s.split(' +  ') if ' +  ' in s else (s, 'Integrated')


def create_custom_AP_list(accessPointsJSON, floorPlansDict, tagKeysDict, simulatedRadioDict, notesDict):
    """Process access points to a structured list."""
    custom_AP_list = []
    for ap in accessPointsJSON['accessPoints']:
        miniTagsDict = {tagKeysDict.get(tag['tagKeyId'], UNKNOWN): tag['value'] for tag in ap.get('tags', [])}
        model, antenna = external_ant_split(ap.get('model', UNKNOWN))
        ap_details = {
            'Name': ap['name'],
            'Floor': floorPlansDict.get(ap['location']['floorPlanId'], UNKNOWN),
            'Model': model,
            'Colour': ekahau_color_dict.get(ap.get('color', 'None'), UNKNOWN),
            'Mounting': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ, {}).get('antennaMounting', ''),
            'AP Bracket': miniTagsDict.get('ap-bracket'),
            'Antenna': antenna,
            'Antenna Bracket': miniTagsDict.get('antenna-bracket'),
            'Antenna Height': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ, {}).get('antennaHeight', ''),
            'Antenna Tilt': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ, {}).get('antennaTilt', ''),
            'Simulated Tx power (5 GHz)': round(simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ, {}).get('transmitPower', 0), 1),
            'RF-Group': miniTagsDict.get('rf-group'),
            'Notes': note_text_processor(ap['noteIds'], notesDict)
        }
        custom_AP_list.append(ap_details)
    return sorted(custom_AP_list, key=lambda x: x['Name'])