# validate_esx.py

from common import load_json
from common import create_floor_plans_dict
from common import create_tag_keys_dict
from common import create_simulated_radios_dict
from common import offender_constructor
from common import create_custom_ap_dict
from common import acceptable_antenna_tilt_angles

from common import FIVE_GHZ_RADIO_ID

nl = '\n'


def validate_color_assignment(offenders, total_ap_count, message_callback):
    if len(offenders.get('color', [])) > 0:
        message_callback(f"{nl}There is a problem! The following {len(offenders.get('color', []))} APs have been assigned no color")
        for ap in offenders['color']:
            message_callback(ap)
        return False
    message_callback(f"{nl}Colour assignment test: PASSED{nl}All {total_ap_count} APs have a non-default colour")
    return True


def validate_height_manipulation(offenders, total_ap_count, message_callback):
    if len(offenders.get('antennaHeight', [])) > 0:
        message_callback(f"{nl}Caution! The following {len(offenders.get('antennaHeight', []))} APs are configured with the Ekahau 'default' height of 2.4 meters, is this intentional?")
        for ap in offenders['antennaHeight']:
            message_callback(ap)
        return True
    message_callback(f"{nl}antennaHeight manipulation test: PASSED{nl}All {total_ap_count} APs have an assigned height other than '2.4' metres")
    return True


def validate_bluetooth_radio_off(offenders, total_ap_count, message_callback):
    if len(offenders.get('bluetooth', [])) > 0:
        message_callback(f"{nl}Caution! The following {len(offenders.get('bluetooth', []))} APs have their Bluetooth radio enabled")
        for ap in offenders['bluetooth']:
            message_callback(ap)
        return False
    message_callback(f"{nl}Bluetooth radio test: PASSED{nl}All {total_ap_count} APs have their Bluetooth radio disabled")
    return True


def validate_required_tags(offenders, total_ap_count, total_required_tag_keys_count, required_tag_keys, message_callback):
    # Initialize a list to store failed tag validations
    pass_required_tag_validation = []

    for missing_tag in offenders['missing_required_tags']:
        if len(offenders.get('missing_required_tags', {}).get(missing_tag, [])) > 0:
            message_callback(
                f"{nl}There is a problem! The following {len(offenders.get('missing_required_tags', {}).get(missing_tag, []))} APs are missing the '{missing_tag}' tag")
            for ap in sorted(offenders['missing_required_tags'][missing_tag]):
                message_callback(ap)
            pass_required_tag_validation.append(False)
        pass_required_tag_validation.append(True)

    if all(pass_required_tag_validation):
        message_callback(f"{nl}Required tag key assignment test: PASSED{nl}")
        for tagKey in required_tag_keys:
            message_callback(f"{tagKey}")
        message_callback(f"{nl}All {total_ap_count} APs have the required {total_required_tag_keys_count} tag keys assigned:")
        return True
    return False

def validate_antenna_tilt(offenders, total_ap_count, message_callback):
    if len(offenders.get('antennaTilt', [])) > 0:
        message_callback(f"{nl}Caution! The following {len(offenders.get('antennaTilt', []))} APs have an antenna tilt that will cause problems when generating per AP installer documentation")
        for ap in offenders['antennaTilt']:
            message_callback(ap)
        return False
    message_callback(f"{nl}Antenna Tilt test: PASSED{nl}All {total_ap_count} APs have a conforming antenna tilt")
    return True

def validate_antenna_mounting_and_tilt_mismatch(offenders, total_ap_count, message_callback):
    if len(offenders.get('antennaMounting_and_antennaTilt_mismatch', [])) > 0:
        message_callback(f"{nl}Caution! The following {len(offenders.get('antennaMounting_and_antennaTilt_mismatch', []))} APs may be configured incorrectly, Wall mounted with 0 degrees of tilt, is this intentional?")
        for ap in offenders['antennaMounting_and_antennaTilt_mismatch']:
            message_callback(ap)
        return False
    message_callback(f"{nl}Antenna Mounting and Tilt Mismatch test: PASSED{nl}All {total_ap_count} APs have a conforming antenna mounting and tilt")
    return True


def validate_esx(working_directory, project_name, message_callback, required_tag_keys, optional_tag_keys):
    message_callback(f'Performing Validation for: {project_name}')

    project_dir = working_directory / project_name

    # Load JSON data
    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    access_points_json = load_json(project_dir, 'accessPoints.json', message_callback)
    simulated_radios_json = load_json(project_dir, 'simulatedRadios.json', message_callback)
    tag_keys_json = load_json(project_dir, 'tagKeys.json', message_callback)

    # Process data
    floor_plans_dict = create_floor_plans_dict(floor_plans_json)
    tag_keys_dict = create_tag_keys_dict(tag_keys_json)
    simulated_radio_dict = create_simulated_radios_dict(simulated_radios_json)

    # Process access points
    custom_ap_dict = create_custom_ap_dict(access_points_json, floor_plans_dict, simulated_radio_dict)

    for ap in access_points_json['accessPoints']:
        for tag in ap['tags']:
            custom_ap_dict[ap['name']]['tags'][tag_keys_dict.get(tag['tagKeyId'])] = tag['value']

    offenders = offender_constructor(required_tag_keys, optional_tag_keys)

    # Count occurrences of each
    for ap in custom_ap_dict.values():

        if ap['color'] == 'none':
            offenders['color'].append(ap['name'])

        if ap['antennaHeight'] == 2.4:
            offenders['antennaHeight'].append(ap['name'])

        for radio in ap['radios'].values():
            if radio.get('radioTechnology') == 'BLUETOOTH' and radio.get('enabled', False):
                offenders['bluetooth'].append(ap['name'])

        if ap.get('radios', {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaTilt') not in acceptable_antenna_tilt_angles:
            offenders['antennaTilt'].append(ap['name'])

        if ap.get('antennaMounting') == 'WALL' and ap.get('radios', {}).get(FIVE_GHZ_RADIO_ID, {}).get('antennaTilt') == 0:
            offenders['antennaMounting_and_antennaTilt_mismatch'].append(ap['name'])

        for tagKey in required_tag_keys:
            if tagKey not in ap['tags']:
                offenders['missing_required_tags'][tagKey].append(ap['name'])

    total_ap_count = len(custom_ap_dict)
    total_required_tag_keys_count = len(required_tag_keys)

    # Perform all validations
    validations = [
        validate_color_assignment(offenders, total_ap_count, message_callback),
        validate_height_manipulation(offenders, total_ap_count, message_callback),
        # validate_bluetooth_radio_off(offenders, total_ap_count, message_callback),
        validate_required_tags(offenders, total_ap_count, total_required_tag_keys_count, required_tag_keys, message_callback),
        validate_antenna_tilt(offenders, total_ap_count, message_callback),
        validate_antenna_mounting_and_tilt_mismatch(offenders, total_ap_count, message_callback)
    ]

    # Print pass/fail states
    if all(validations):
        message_callback(f"{nl}Validation PASSED!")
    else:
        message_callback(f"{nl}Validation FAILED")
    return
