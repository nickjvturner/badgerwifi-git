# validate_esx.py

from collections import defaultdict

from common import load_json
from common import create_floor_plans_dict
from common import create_tag_keys_dict
from common import create_simulated_radios_dict
from common import offender_constructor
from common import create_custom_ap_dict

from common import FIVE_GHZ_RADIO_ID, UNKNOWN


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


def validate_required_tags(offenders, total_ap_count, totalRequiredTagKeysCount, requiredTagKeys, message_callback):
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
        for tagKey in requiredTagKeys:
            message_callback(f"{tagKey}")
        message_callback(f"{nl}All {total_ap_count} APs have the required {totalRequiredTagKeysCount} tag keys assigned:")
        return True
    return False

def validate_esx(working_directory, project_name, message_callback, requiredTagKeys, optionalTagKeys):
    message_callback(f'Performing Validation for: {project_name}')

    project_dir = working_directory / project_name

    # Load JSON data
    floorPlansJSON = load_json(project_dir, 'floorPlans.json', message_callback)
    accessPointsJSON = load_json(project_dir, 'accessPoints.json', message_callback)
    simulatedRadiosJSON = load_json(project_dir, 'simulatedRadios.json', message_callback)
    tagKeysJSON = load_json(project_dir, 'tagKeys.json', message_callback)

    # Process data
    floorPlansDict = create_floor_plans_dict(floorPlansJSON)
    tagKeysDict = create_tag_keys_dict(tagKeysJSON)
    simulatedRadioDict = create_simulated_radios_dict(simulatedRadiosJSON)

    # Process access points
    custom_ap_dict = create_custom_ap_dict(accessPointsJSON, floorPlansDict, simulatedRadioDict)

    for ap in accessPointsJSON['accessPoints']:
        for tag in ap['tags']:
            custom_ap_dict[ap['name']]['tags'][tagKeysDict.get(tag['tagKeyId'])] = tag['value']

    offenders = offender_constructor(requiredTagKeys, optionalTagKeys)
    count = 0
    # Count occurrences of each
    for ap in custom_ap_dict.values():

        if ap['color'] == 'none':
            offenders['color'].append(ap['name'])

        if ap['antennaHeight'] == 2.4:
            offenders['antennaHeight'].append(ap['name'])

        for radio in ap['radios'].values():
            if radio.get('radioTechnology') == 'BLUETOOTH' and radio.get('enabled', False):
                offenders['bluetooth'].append(ap['name'])


        for tagKey in requiredTagKeys:
            if tagKey not in ap['tags']:
                offenders['missing_required_tags'][tagKey].append(ap['name'])



    total_ap_count = len(custom_ap_dict)
    totalRequiredTagKeysCount = len(requiredTagKeys)

    # Perform all validations
    validations = [
        validate_color_assignment(offenders, total_ap_count, message_callback),
        validate_height_manipulation(offenders, total_ap_count, message_callback),
        # validate_bluetooth_radio_off(offenders, total_ap_count, message_callback),
        validate_required_tags(offenders, total_ap_count, totalRequiredTagKeysCount, requiredTagKeys, message_callback)
    ]

    # Print pass/fail states
    if all(validations):
        message_callback(f"{nl}Validation PASSED!")
    else:
        message_callback(f"{nl}Validation FAILED")
    return
