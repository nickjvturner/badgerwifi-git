# required_tags.py

UNKNOWN = 'Unknown'
FIVE_GHZ = 'FIVE'

from common import ekahau_color_dict
from common import external_ant_split
from common import note_text_processor

# Project A
###########

requiredTagKeys = ("ap-bracket", "antenna-bracket", "rf-group")

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


# Project B
###########

# requiredTagKeys = ("ap-bracket", "UNIT", "EX", "ind/out", "power", "backhaul")
# optionalTagKeys = ("building-group", 'sequence-override')
#
# def create_custom_AP_list(accessPointsJSON, floorPlansDict, tagKeysDict, simulatedRadioDict, notesDict):
#     """Process access points to a structured list."""
#     custom_AP_list = []
#     for ap in accessPointsJSON['accessPoints']:
#         miniTagsDict = {tagKeysDict.get(tag['tagKeyId'], UNKNOWN): tag['value'] for tag in ap.get('tags', [])}
#         model, antenna = external_ant_split(ap.get('model', UNKNOWN))
#         ap_details = {
#             'Name': ap['name'],
#             'Hostname': '',
#             'Colour': ekahau_color_dict.get(ap.get('color', 'None'), UNKNOWN),
#             'Floor': floorPlansDict.get(ap['location']['floorPlanId'], UNKNOWN),
#             'Model': model + 'EX' if miniTagsDict.get('EX') == 'YES' else model,
#             'Mounting': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ, {}).get('antennaMounting', ''),
#             'Antenna Height': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ, {}).get('antennaHeight', ''),
#             'Antenna Tilt': simulatedRadioDict.get(ap['id'], {}).get(FIVE_GHZ, {}).get('antennaTilt', ''),
#             'UNIT': miniTagsDict.get('UNIT'),
#             'EX': miniTagsDict.get('EX'),
#             'Mount': miniTagsDict.get('ap-bracket'),
#             'ind/out': miniTagsDict.get('ind/out'),
#             'power source': miniTagsDict.get('power'),
#             'building-group': miniTagsDict.get('building-group'),
#             'Notes': note_text_processor(ap['noteIds'], notesDict)
#         }
#         custom_AP_list.append(ap_details)
#     return sorted(custom_AP_list, key=lambda x: x['Name'])


# Project C
###########

# required_tagKeys = ("ap-bracket", "antenna-bracket", "rf-group")



def offender_constructor():
    offenders = {
        'color': [],
        'antennaHeight': [],
        'missing_tags': {}
    }

    for tagKey in requiredTagKeys:
        offenders['missing_tags'][tagKey] = []

    return offenders