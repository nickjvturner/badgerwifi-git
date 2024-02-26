# validate_esx.py

from collections import defaultdict

from root_common import load_json
from root_common import create_floor_plans_dict
from root_common import create_tag_keys_dict
from root_common import create_simulated_radios_dict
from root_common import model_antenna_split
from root_common import offender_constructor

nl = '\n'


def validate_color_assignment(offenders, message_callback):
    if len(offenders.get('color', [])) > 0:
        message_callback(f"{nl}There is a problem! The following {len(offenders.get('color', []))} APs have been assigned no color")
        for ap in offenders['color']:
            message_callback(ap)
        return False
    message_callback(f"{nl}Colour assignment test: PASSED")
    return True


def validate_height_manipulation(offenders, message_callback):
    if len(offenders.get('antennaHeight', [])) > 0:
        message_callback(f"{nl}There is a problem! The following {len(offenders.get('antennaHeight', []))} APs are configured with the Ekahau default height of 2.4 meters, is that intentional?")
        for ap in offenders['antennaHeight']:
            message_callback(ap)
        return False
    message_callback(f"{nl}Height assignment test: PASSED")
    return True


def validate_tags(offenders, message_callback):
    # Initialize a list to store failed tag validations
    pass_required_tag_validation = []

    for missing_tag in offenders['missing_tags']:
        if len(offenders.get('missing_tags', {}).get(missing_tag, [])) > 0:
            message_callback(
                f"{nl}There is a problem! The following {len(offenders.get('missing_tags', {}).get(missing_tag, []))} APs are missing the '{missing_tag}' tag")
            for ap in sorted(offenders['missing_tags'][missing_tag]):
                message_callback(ap)
            pass_required_tag_validation.append(False)
        pass_required_tag_validation.append(True)

    if all(pass_required_tag_validation):
        message_callback(f"{nl}Required tags assignment test: PASSED")
        return True
    return False

def validate_esx(working_directory, project_name, message_callback, requiredTagKeys, optionalTagKeys):
    message_callback(f'Performing Validation for: {project_name}')

    project_dir = working_directory / project_name

    # Load JSON data
    floorPlansJSON = load_json(project_dir, 'floorPlans.json')
    accessPointsJSON = load_json(project_dir, 'accessPoints.json')
    simulatedRadiosJSON = load_json(project_dir, 'simulatedRadios.json')
    tagKeysJSON = load_json(project_dir, 'tagKeys.json')

    # Process data
    floorPlansDict = create_floor_plans_dict(floorPlansJSON)
    tagKeysDict = create_tag_keys_dict(tagKeysJSON)
    simulatedRadioDict = create_simulated_radios_dict(simulatedRadiosJSON)

    # Process access points
    processedAPdict = {}
    for ap in accessPointsJSON['accessPoints']:
        ap_model, external_antenna, antenna_description = model_antenna_split(ap.get('model', ''))

        processedAPdict[ap['name']] = {
        'name': ap['name'],
        'color': ap.get('color', 'none'),
        'model': ap_model,
        'antenna': external_antenna,
        'floor': floorPlansDict.get(ap['location']['floorPlanId'], ''),
        'antennaTilt': simulatedRadioDict.get(ap['id'], {}).get('antennaTilt', ''),
        'antennaMounting': simulatedRadioDict.get(ap['id'], {}).get('antennaMounting', ''),
        'antennaHeight': simulatedRadioDict.get(ap['id'], {}).get('antennaHeight', ''),
        'remarks': '',
        'ap bracket': '',
        'antenna bracket': '',
        'tags': {}
        }

        for tag in ap['tags']:
            processedAPdict[ap['name']]['tags'][tagKeysDict.get(tag['tagKeyId'])] = tag['value']

    # Initialize defaultdicts to count attributes
    color_counts = defaultdict(int)
    antennaHeight_counts = defaultdict(int)

    tag_counts = defaultdict(int)

    model_counts = defaultdict(int)

    offenders = offender_constructor(requiredTagKeys)

    # Count occurrences of each
    for ap in processedAPdict.values():

        color_counts[ap['color']] += 1
        if ap['color'] == 'none':
            offenders['color'].append(ap['name'])

        antennaHeight_counts[ap['antennaHeight']] += 1
        if ap['antennaHeight'] == 2.4:
            offenders['antennaHeight'].append(ap['name'])

        # Iterate through the tags dictionary within each AP
        for tag_key, tag_value in ap['tags'].items():
            tag_counts[(tag_key, tag_value)] += 1

        for tagKey in requiredTagKeys:
            if tagKey not in ap['tags']:
                offenders['missing_tags'][tagKey].append(ap['name'])

        model_counts[ap['model']] += 1


    # Perform all validations
    validations = [
        validate_color_assignment(offenders, message_callback),
        validate_height_manipulation(offenders, message_callback),
        validate_tags(offenders, message_callback)
    ]

    # Print pass/fail states
    if all(validations):
        message_callback(f"{nl}Validation PASSED!")
    else:
        message_callback(f"{nl}Validation FAILED")
    return
