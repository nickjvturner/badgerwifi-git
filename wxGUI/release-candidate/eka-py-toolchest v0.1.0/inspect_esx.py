# inspect_esx.py

import json
from collections import defaultdict
from pathlib import Path

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

def inspect(file_path, message_callback):
    file = Path(file_path)
    message_callback('Performing action for: ' + file.name)
    project_name = file.stem
    message_callback('Project name: ' + project_name)
    working_directory = file.parent
    message_callback('Working directory: ' + str(working_directory))

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

    offenders = {
        'color': [],
        'antennaHeight': [],
        'missing_tags': {
            'ap-bracket': [],
            'antenna-bracket': [],
            'rf-group': []
        }
    }

    required_tagKeys = ("ap-bracket", "antenna-bracket", "rf-group")

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

        for tagKey in required_tagKeys:
            if tagKey not in ap['tags']:
                offenders['missing_tags'][tagKey].append(ap['name'])

        model_counts[ap['model']] += 1


    # Print the count of each tag key and value pair, sorted
    # print(f"{nl}Count of each tag key and value pair:")
    # for (tag_key, tag_value), count in sorted(tag_counts.items()):
    #     print(f"{tag_key}: {tag_value} - {count}")

    # Validation

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
