# common.py

import json
from pathlib import Path


# Constants
VERSION = '1.2'
UNKNOWN = 'Unknown'
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

def create_floor_plans_height_dict(floorPlansJSON):
    """Create a dictionary of floor plans."""
    floorPlansDict = {}
    for floor in floorPlansJSON['floorPlans']:
        floorPlansDict[floor['id']] = floor['height']
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
            # Attempt to retrieve the note by ID and its 'text' field
            note = notesDict.get(noteId, {})
            text = note.get('text', None)  # Use None as the default

            # Append the text to notes_text only if it exists and is not empty
            if text:  # This condition is True if text is not None and not an empty string
                notes_text.append(text)

        return '\n'.join(notes_text)  # Join all non-empty note texts into a single string
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


def offender_constructor(requiredTagKeys):
    offenders = {
        'color': [],
        'antennaHeight': [],
        'missing_tags': {}
    }

    for tagKey in requiredTagKeys:
        offenders['missing_tags'][tagKey] = []

    return offenders