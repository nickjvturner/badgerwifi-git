from common import model_antenna_split
from common import ekahau_color_dict
from common import note_text_processor

from common import extract_frequency_channel_and_width
from common import get_ssid_and_mac
from common import wifi_channel_dict
from common import get_security_and_technologies

from common import UNKNOWN, FIVE_GHZ_RADIO_ID

requiredTagKeys = ()
optionalTagKeys = ()


def create_custom_ap_list(access_points_json, floor_plans_dict, tag_keys_dict, simulated_radio_dict, antenna_types_dict, notes_dict):
    """Process access points to a structured list."""
    custom_ap_list = []
    for ap in access_points_json['accessPoints']:
        model, antenna, antenna_description = model_antenna_split(ap.get('model', UNKNOWN))
        ap_details = {
            'Name': ap['name'],
            'Colour': ekahau_color_dict.get(ap.get('color', 'None'), UNKNOWN),
            'Floor': floor_plans_dict.get(ap['location']['floorPlanId']).get('name'),
            'Model': model,
            'Antenna': antenna,
            'Antenna Description': antenna_description,
            'Mounting': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaMounting', ''),
            'Antenna Height': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaHeight', ''),
            'Antenna Tilt': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaTilt', ''),
            'Notes': note_text_processor(ap['noteIds'], notes_dict)
        }
        custom_ap_list.append(ap_details)
    return sorted(custom_ap_list, key=lambda x: x['Name'])


def create_custom_measured_ap_list(access_points_json, floor_plans_dict, tag_keys_dict, measured_radios_dict, notes_dict):
    """Process access points to a structured list."""

    surveyed_ap_list = []

    for ap in access_points_json['accessPoints']:

        mini_tags_dict = {tag_keys_dict.get(tag['tagKeyId'], UNKNOWN): tag['value'] for tag in ap.get('tags', [])}

        measured_radios = measured_radios_dict.get(ap['id'], {})

        ap_details = {
            'Name': ap['name'],
            'Vendor': ap.get('vendor', UNKNOWN),
            '-   ': '',
            '2.4 GHz': extract_frequency_channel_and_width(measured_radios, 'two')[0][1],
            '2.4 Ch Primary': wifi_channel_dict.get(extract_frequency_channel_and_width(measured_radios, 'two')[0][0], ''),
            '2.4 Width': extract_frequency_channel_and_width(measured_radios, 'two')[0][2],
            '2.4 SSIDs': get_ssid_and_mac(measured_radios.get('two', {})),
            '2.4 Security / Standards': get_security_and_technologies(measured_radios.get('two', {})),
            ' -  ': '',
            '5 GHz': extract_frequency_channel_and_width(measured_radios, 'five')[0][1],
            '5 Ch Primary': wifi_channel_dict.get(extract_frequency_channel_and_width(measured_radios, 'five')[0][0], ''),
            '5 Width': extract_frequency_channel_and_width(measured_radios, 'five')[0][2],
            '5 SSIDs': get_ssid_and_mac(measured_radios.get('five', {})),
            '5 Security / Standards': get_security_and_technologies(measured_radios.get('five', {})),
            '  - ': '',
            '6 GHz': extract_frequency_channel_and_width(measured_radios, 'six')[0][1],
            '6 Ch Primary': wifi_channel_dict.get(extract_frequency_channel_and_width(measured_radios, 'six')[0][0], ''),
            '6 Width': extract_frequency_channel_and_width(measured_radios, 'six')[0][2],
            '6 SSIDs': get_ssid_and_mac(measured_radios.get('six', {})),
            '6 Security / Standards': get_security_and_technologies(measured_radios.get('six', {})),
            '   -': '',
            'Colour': ekahau_color_dict.get(ap.get('color', 'None'), UNKNOWN),
            'Floor': floor_plans_dict.get(ap.get('location', {}).get('floorPlanId'), {}).get('name', UNKNOWN),
            'flagged as My AP': ap.get('mine', UNKNOWN),
            'hidden': ap.get('hidden', UNKNOWN),
            'manually positioned': ap.get('userDefinedPosition', UNKNOWN),
            'Notes': note_text_processor(ap['noteIds'], notes_dict)
        }
        surveyed_ap_list.append(ap_details)
    return sorted(surveyed_ap_list, key=lambda x: x['Name'])
