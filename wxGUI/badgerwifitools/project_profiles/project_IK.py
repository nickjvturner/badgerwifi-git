# project_IK.py

from common import model_antenna_split
from common import ekahau_color_dict
from common import note_text_processor

from common import UNKNOWN, FIVE_GHZ_RADIO_ID

requiredTagKeys = ("ap-bracket", "antenna-bracket", "rf-group")
optionalTagKeys = ()

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
def create_custom_ap_list(access_points_json, floor_plans_dict, tag_keys_dict, simulated_radio_dict, notes_dict):
    """Process access points to a structured list."""
    custom_ap_list = []
    for ap in access_points_json['accessPoints']:
        mini_tags_dict = {tag_keys_dict.get(tag['tagKeyId'], UNKNOWN): tag['value'] for tag in ap.get('tags', [])}
        model, antenna, antenna_description = model_antenna_split(ap.get('model', UNKNOWN))
        ap_details = {
            'Name': ap['name'],
            'Floor': floor_plans_dict.get(ap['location']['floorPlanId']).get('name'),
            'Model': model,
            'Colour': ekahau_color_dict.get(ap.get('color', 'None'), UNKNOWN),
            'Mounting': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaMounting', ''),
            'AP Bracket': mini_tags_dict.get('ap-bracket', UNKNOWN),
            'Antenna': antenna,
            'Antenna Description': antenna_description,
            'Antenna Bracket': mini_tags_dict.get('antenna-bracket', UNKNOWN),
            'Antenna Height': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaHeight', ''),
            'Antenna Tilt': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaTilt', ''),
            'Simulated Tx power (5 GHz)': round(simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('transmitPower', 0), 1),
            'RF-Group': mini_tags_dict.get('rf-group', UNKNOWN),
            'Notes': note_text_processor(ap['noteIds'], notes_dict)
        }
        custom_ap_list.append(ap_details)
    return sorted(custom_ap_list, key=lambda x: x['Name'])
