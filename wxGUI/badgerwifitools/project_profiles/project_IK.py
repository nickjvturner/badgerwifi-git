# project_IK.py

from common import ekahau_color_dict
from common import note_text_processor
from common import antenna_name_cleanup
from common import extract_frequency_channel_and_width
from common import get_ssid_and_mac
from common import get_security_and_technologies
from common import get_supported_rates_from_ies
from common import get_tx_power_from_ies
from common import wifi_channel_dict
from common import get_channel_from_ies
from common import get_wifi_band_from_ie_channel

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

# PDS Project Creator
predictive_json_asset_deletion = [
    "accessPoints",
    "simulatedRadios",
    "tagKeys",
    "wallPoints",
    "WallSegments",
    "attenuationAreas",
]


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
            'Antenna Height (m)': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaHeight', ''),
            'Antenna Tilt (degrees)': simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaTilt', ''),
            'Simulated Tx power (5 GHz), dBm': round(simulated_radio_dict.get(ap['id'], {}).get(FIVE_GHZ_RADIO_ID, {}).get('transmitPower', 0), 1),
            'RF-Group': mini_tags_dict.get('rf-group', UNKNOWN),
            'Notes': note_text_processor(ap['noteIds'], notes_dict),
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
            '2.4 Tx Power': get_tx_power_from_ies(measured_radios.get('two', {})),
            '2.4 Supported Rates': get_supported_rates_from_ies(measured_radios.get('two', {})),
            ' -  ': '',
            '5 GHz': extract_frequency_channel_and_width(measured_radios, 'five')[0][1],
            '5 Ch Primary': wifi_channel_dict.get(extract_frequency_channel_and_width(measured_radios, 'five')[0][0], ''),
            '5 Width': extract_frequency_channel_and_width(measured_radios, 'five')[0][2],
            '5 SSIDs': get_ssid_and_mac(measured_radios.get('five', {})),
            '5 Security / Standards': get_security_and_technologies(measured_radios.get('five', {})),
            '5 Channel from IEs': get_channel_from_ies(measured_radios.get('five', {})),
            '5 WiFi Band': get_wifi_band_from_ie_channel(measured_radios.get('five', {})),
            '5 Tx Power': get_tx_power_from_ies(measured_radios.get('five', {})),
            '5 Supported Rates': get_supported_rates_from_ies(measured_radios.get('five', {})),
            '  - ': '',
            '6 GHz': extract_frequency_channel_and_width(measured_radios, 'six')[0][1],
            '6 Ch Primary': wifi_channel_dict.get(extract_frequency_channel_and_width(measured_radios, 'six')[0][0], ''),
            '6 Width': extract_frequency_channel_and_width(measured_radios, 'six')[0][2],
            '6 SSIDs': get_ssid_and_mac(measured_radios.get('six', {})),
            '6 Security / Standards': get_security_and_technologies(measured_radios.get('six', {})),
            '6 Tx Power': get_tx_power_from_ies(measured_radios.get('six', {})),
            '6 Supported Rates': get_supported_rates_from_ies(measured_radios.get('six', {})),
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
