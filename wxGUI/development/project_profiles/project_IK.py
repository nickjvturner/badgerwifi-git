# project_IK.py

from common import model_antenna_split
from common import ekahau_color_dict
from common import note_text_processor

from common import UNKNOWN, FIVE_GHZ_RADIO_ID

requiredTagKeys = ("ap-bracket", "antenna-bracket", "rf-group")
optionalTagKeys = ()

acceptableAntennaTiltAngles = (-10, -20, -30, -40, -45, -50, -60, -70, -80, -90)

project_specific_conventions = {
    "AP-514": {
        "color": "red",
        "mounting": "CEILING",
        "antennaHeightGreater than": 5
    },
    "AP-655": {
        "color": "orange",
        "mounting": "CEILING",
        "antennaHeightGreater than": 2
    }
}

# Custom AP List Constructor
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
            'Mounting': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaMounting', ''),
            'AP Bracket': 'not-required' if miniTagsDict.get('ap-bracket') else miniTagsDict.get('ap-bracket'),
            'Antenna': antenna,
            'Antenna Description': antenna_description,
            'Antenna Bracket': miniTagsDict.get('antenna-bracket'),
            'Antenna Height': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaHeight', ''),
            'Antenna Tilt': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaTilt', ''),
            'Simulated Tx power (5 GHz)': round(simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('transmitPower', 0), 1),
            'RF-Group': miniTagsDict.get('rf-group'),
            'Notes': note_text_processor(ap['noteIds'], notesDict)
        }
        custom_AP_list.append(ap_details)
    return sorted(custom_AP_list, key=lambda x: x['Name'])
