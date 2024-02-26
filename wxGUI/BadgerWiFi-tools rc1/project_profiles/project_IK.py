# project_IK.py

from root_common import model_antenna_split
from root_common import ekahau_color_dict
from root_common import note_text_processor

# CONSTANTS
UNKNOWN = 'Unknown'
FIVE_GHZ = 'FIVE'

requiredTagKeys = ("ap-bracket", "antenna-bracket", "rf-group")
optionalTagKeys = ()

def create_custom_AP_list(accessPointsJSON, floorPlansDict, tagKeysDict, simulatedRadioDict, notesDict):
    """Process access points to a structured list."""
    custom_AP_list = []
    for ap in accessPointsJSON['accessPoints']:
        miniTagsDict = {tagKeysDict.get(tag['tagKeyId'], UNKNOWN): tag['value'] for tag in ap.get('tags', [])}
        model, antenna, antenna_description = model_antenna_split(ap.get('model', UNKNOWN))
        ap_details = {
            'Name': ap['name'],
            'Floor': floorPlansDict.get(ap['location']['floorPlanId'], UNKNOWN),
            'Model': model,
            'Colour': ekahau_color_dict.get(ap.get('color', 'None'), UNKNOWN),
            'Mounting': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ, {}).get('antennaMounting', ''),
            'AP Bracket': miniTagsDict.get('ap-bracket'),
            'Antenna': antenna,
            'Antenna Description': antenna_description,
            'Antenna Bracket': miniTagsDict.get('antenna-bracket'),
            'Antenna Height': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ, {}).get('antennaHeight', ''),
            'Antenna Tilt': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ, {}).get('antennaTilt', ''),
            'Simulated Tx power (5 GHz)': round(simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ, {}).get('transmitPower', 0), 1),
            'RF-Group': miniTagsDict.get('rf-group'),
            'Notes': note_text_processor(ap['noteIds'], notesDict)
        }
        custom_AP_list.append(ap_details)
    return sorted(custom_AP_list, key=lambda x: x['Name'])
