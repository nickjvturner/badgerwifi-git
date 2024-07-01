from common import model_antenna_split
from common import ekahau_color_dict
from common import note_text_processor

from common import UNKNOWN, FIVE_GHZ_RADIO_ID

requiredTagKeys = ("ap-bracket", "UNIT", "EX", "ind/out", "power", "backhaul")
optionalTagKeys = ("building-group", 'sequence-override')

preferred_ap_rename_script = 'Dynamic Rows'


def create_custom_ap_list(access_points_json, floor_plans_dict, tag_keys_dict, simulated_radio_dict, antenna_types_dict, notes_dict):
    """Process access points to a structured list."""
    custom_ap_list = []
    for ap in access_points_json['accessPoints']:
        mini_tags_dict = {tag_keys_dict.get(tag['tagKeyId'], UNKNOWN): tag['value'] for tag in ap.get('tags', [])}
        model, antenna, antenna_description = model_antenna_split(ap.get('model', UNKNOWN))
        ap_details = {
            'Name': ap['name'],
            'Hostname': '',
            'Colour': ekahau_color_dict.get(ap.get('color', 'None'), UNKNOWN),
            'Floor': floor_plans_dict.get(ap['location']['floorPlanId']).get('name'),
            'Model': model + 'EX' if mini_tags_dict.get('EX') == 'YES' else model,
            'Mounting': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaMounting', ''),
            'Antenna Height': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaHeight', ''),
            'Antenna Tilt': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaTilt', ''),
            'UNIT': mini_tags_dict.get('UNIT'),
            'EX': mini_tags_dict.get('EX'),
            'Mount': mini_tags_dict.get('ap-bracket'),
            'ind/out': mini_tags_dict.get('ind/out'),
            'power source': mini_tags_dict.get('power'),
            'backhaul': mini_tags_dict.get('backhaul'),
            'building-group': mini_tags_dict.get('building-group'),
            'Notes': note_text_processor(ap['noteIds'], notes_dict)
        }
        custom_ap_list.append(ap_details)
    return sorted(custom_ap_list, key=lambda x: x['Name'])
