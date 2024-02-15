# inspect_esx.py

import json
from collections import defaultdict
from pathlib import Path
from common import ekahau_color_dict
from configuration.requiredTagKeys import requiredTagKeys
from configuration.requiredTagKeys import offender_constructor

nl = '\n'

def validate_color_assignment(offenders, message_callback):
    if len(offenders.get('color', [])) > 0:
        message_callback(f"{nl}There is a problem! The following {len(offenders.get('color', []))} APs have been assigned no color")
        for ap in offenders['color']:
            message_callback(ap)
        return False
    return True


def validate_height_manipulation(offenders, message_callback):
    if len(offenders.get('antennaHeight', [])) > 0:
        message_callback(f"{nl}There is a problem! The following {len(offenders.get('antennaHeight', []))} APs are configured with the Ekahau default height of 2.4 meters, is that intentional?")
        for ap in offenders['antennaHeight']:
            message_callback(ap)
        return False
    return True


def validate_tags(offenders, message_callback):
    # Initialize a list to store failed tag validations
    pass_required_tag_validation = []

    for missing_tag in offenders['missing_tags']:
        if len(offenders.get('missing_tags', {}).get(missing_tag, [])) > 0:
            message_callback(
                f"{nl}There is a problem! The following {len(offenders.get('missing_tags', {}).get(missing_tag, []))} APs are missing the '{missing_tag}' tag")
            for ap in offenders['missing_tags'][missing_tag]:
                message_callback(ap)
            pass_required_tag_validation.append(False)
        pass_required_tag_validation.append(True)

    if pass_required_tag_validation:
        return True
    return False

def summarise(working_directory, project_name, message_callback):
    message_callback(f'Summarising the Contents of: {project_name}{nl}')

    # Load the floorPlans.json file into the floorPlansJSON Dictionary
    with open(working_directory / project_name / 'floorPlans.json') as json_file:
        floorPlansJSON = json.load(json_file)

    # Create dictionary for the floor plans
    floorPlansDict = {floor['id']: floor['name'] for floor in floorPlansJSON['floorPlans']}

    # Load the accessPoints.json file into the accessPointsJSON dictionary
    with open(working_directory / project_name / 'accessPoints.json') as json_file:
        accessPointsJSON = json.load(json_file)

    # Load the simulatedRadios.json file into the simulatedRadios dictionary
    with open(working_directory / project_name / 'simulatedRadios.json') as json_file:
        simulatedRadiosJSON = json.load(json_file)

    # Create dictionary for simulated radios
    simulatedRadioDict = {radio['accessPointId']: {x: y for x, y in radio.items()} for radio in simulatedRadiosJSON['simulatedRadios']}

    def externalAntSplitAnt(model_string):
        return model_string.split(' +  ')[1] if ' +  ' in model_string else 'integrated'

    def externalAntSplitModel(model_string):
        return model_string.split(' +  ')[0] if ' +  ' in model_string else model_string

    # Load takKeys JSON
    with open(working_directory / project_name / 'tagKeys.json') as json_file:
        tagKeysJSON = json.load(json_file)

    # Create restructured dictionary for the tagKeys
    tagKeysDict = {tagKey['id']: tagKey['key'] for tagKey in tagKeysJSON['tagKeys']}

    # Process access points
    processedAPdict = {}
    for ap in accessPointsJSON['accessPoints']:
        processedAPdict[ap['name']] = {
            'name': ap['name'],
            'color': ap.get('color', 'none'),
            'model': externalAntSplitModel(ap.get('model', '')),
            'antenna': externalAntSplitAnt(ap.get('model', '')),
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

    # Initialize defaultdict to count attributes
    color_counts = defaultdict(int)
    antennaHeight_counts = defaultdict(int)

    tag_counts = defaultdict(int)

    model_counts = defaultdict(int)

    offenders = offender_constructor()

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

    # Prepare the summary message
    summary_message = f"Count of each model type:{nl}"
    for model, count in sorted(model_counts.items()):
        summary_message += f"{model}: {count}{nl}"

    summary_message += f"{nl}Count of each color:{nl}"
    for color, count in sorted(color_counts.items()):
        summary_message += f"{ekahau_color_dict.get(color)}: {count}{nl}"

    summary_message += f"{nl}Count of each AP height:{nl}"
    for height, count in sorted(antennaHeight_counts.items()):
        summary_message += f"{height}: {count}{nl}"

    # Print the count of each tag key and value pair, sorted
    summary_message += f"{nl}Count of each tag key and value pair:{nl}"
    for (tag_key, tag_value), count in sorted(tag_counts.items()):
        summary_message += f"{tag_key} - {tag_value}: {count}{nl}"

    message_callback(summary_message)
