# project_IK.py

from root_common import model_antenna_split
from root_common import ekahau_color_dict
from root_common import note_text_processor

# CONSTANTS
UNKNOWN = 'Unknown'
FIVE_GHZ = 'FIVE'

requiredTagKeys = ("ap-bracket", "UNIT", "EX", "ind/out", "power", "backhaul")
optionalTagKeys = ("building-group", 'sequence-override')

def create_custom_AP_list(accessPointsJSON, floorPlansDict, tagKeysDict, simulatedRadioDict, notesDict):
    """Process access points to a structured list."""
    custom_AP_list = []
    for ap in accessPointsJSON['accessPoints']:
        miniTagsDict = {tagKeysDict.get(tag['tagKeyId'], UNKNOWN): tag['value'] for tag in ap.get('tags', [])}
        model, antenna, antenna_description = model_antenna_split(ap.get('model', UNKNOWN))
        ap_details = {
            'Name': ap['name'],
            'Hostname': '',
            'Colour': ekahau_color_dict.get(ap.get('color', 'None'), UNKNOWN),
            'Floor': floorPlansDict.get(ap['location']['floorPlanId'], UNKNOWN),
            'Model': model + 'EX' if miniTagsDict.get('EX') == 'YES' else model,
            'Mounting': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ, {}).get('antennaMounting', ''),
            'Antenna Height': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ, {}).get('antennaHeight', ''),
            'Antenna Tilt': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ, {}).get('antennaTilt', ''),
            'UNIT': miniTagsDict.get('UNIT'),
            'EX': miniTagsDict.get('EX'),
            'Mount': miniTagsDict.get('ap-bracket'),
            'ind/out': miniTagsDict.get('ind/out'),
            'power source': miniTagsDict.get('power'),
            'building-group': miniTagsDict.get('building-group'),
            'Notes': note_text_processor(ap['noteIds'], notesDict)
        }
        custom_AP_list.append(ap_details)
    return sorted(custom_AP_list, key=lambda x: x['Name'])
