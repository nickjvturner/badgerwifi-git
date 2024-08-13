# project_IK.py

from common import ekahau_color_dict
from common import note_text_processor
from common import antenna_name_cleanup

from common import UNKNOWN, FIVE_GHZ_RADIO_ID

requiredTagKeys = ("ap-bracket", "antenna-bracket", "rf-group")
optionalTagKeys = ()

preferred_ap_rename_script = 'Dynamic Rows'

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


def meters_to_feet_inches(meters):
    # 1 meter = 3.28084 feet
    total_inches = meters * 39.3701
    feet = int(total_inches // 12)
    inches = total_inches % 12
    return f'''{feet}' {inches:0f}" '''

# Custom AP List Constructor
def create_custom_ap_list(access_points_json, floor_plans_dict, tag_keys_dict, simulated_radio_dict, antenna_types_dict, notes_dict):
    """Process access points to a structured list."""
    custom_ap_list = []
    for ap in access_points_json['accessPoints']:
        mini_tags_dict = {tag_keys_dict.get(tag['tagKeyId'], UNKNOWN): tag['value'] for tag in ap.get('tags', [])}
        antenna_type_detail = antenna_types_dict.get(simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaTypeId'))
        antenna_name = antenna_name_cleanup(antenna_type_detail.get('name'))
        ap_details = {
            'Name': ap['name'],
            'Floor': floor_plans_dict.get(ap['location']['floorPlanId']).get('name'),
            'Model': ap.get('vendor') + ' ' + ap.get('model'),
            'Colour': ekahau_color_dict.get(ap.get('color', 'None'), UNKNOWN),
            'Mounting': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaMounting', ''),
            'AP Bracket': mini_tags_dict.get('ap-bracket', UNKNOWN),
            'Antenna': antenna_name if antenna_type_detail.get('apCoupling') == 'EXTERNAL_ANTENNA' else 'not-required',
            'Antenna Description': antenna_type_detail.get('apCoupling'),
            'Antenna Bracket': mini_tags_dict.get('antenna-bracket', UNKNOWN),
            'Antenna Height (ft)': meters_to_feet_inches((simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaHeight', ''))),
            'Antenna Tilt (degrees)': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaTilt', ''),
            'Simulated Tx power (5 GHz), dBm': round(simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('transmitPower', 0), 1),
            'RF-Group': mini_tags_dict.get('rf-group', UNKNOWN),
            'Notes': note_text_processor(ap['noteIds'], notes_dict),
        }
        custom_ap_list.append(ap_details)
    return sorted(custom_ap_list, key=lambda x: x['Name'])
