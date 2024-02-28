# summarise_esx_.py

from collections import defaultdict

from common import load_json
from common import create_floor_plans_dict
from common import create_tag_keys_dict
from common import create_simulated_radios_dict

from common import offender_constructor
from common import create_custom_ap_dict

# CONSTANTS
nl = '\n'
from common import ekahau_color_dict


def summarise_esx(working_directory, project_name, message_callback, requiredTagKeys, optionalTagKeys):
    message_callback(f'Summarising the Contents of: {project_name}{nl}')

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
    custom_ap_dict = create_custom_ap_dict(accessPointsJSON, floorPlansDict, simulatedRadioDict)

    for ap in accessPointsJSON['accessPoints']:
        for tag in ap['tags']:
            custom_ap_dict[ap['name']]['tags'][tagKeysDict.get(tag['tagKeyId'])] = tag['value']

    # Initialize defaultdict to count attributes
    color_counts = defaultdict(int)
    antennaHeight_counts = defaultdict(int)

    tag_counts = defaultdict(int)

    model_counts = defaultdict(int)

    offenders = offender_constructor(requiredTagKeys, optionalTagKeys)

    # Count occurrences of each
    for ap in custom_ap_dict.values():

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
                offenders['missing_required_tags'][tagKey].append(ap['name'])

        model_counts[ap['model']] += 1

    # Prepare the summary message
    summary_message = f"Count of each model type:{nl}"
    for model, count in sorted(model_counts.items()):
        summary_message += f"{model}: {count}{nl}"

    summary_message += f"{nl}{nl}Count of each color:{nl}"
    color_counts_sorted = sorted(color_counts.items(), key=lambda item: ekahau_color_dict.get(item[0], item[0]))
    for color, count in color_counts_sorted:
        summary_message += f"{ekahau_color_dict.get(color)}: {count}{nl}"

    summary_message += f"{nl}Count of each AP height:{nl}"
    for height, count in sorted(antennaHeight_counts.items()):
        summary_message += f"{height}: {count}{nl}"

    # Print the count of each tag key and value pair, sorted
    summary_message += f"{nl}Count of each tag key and value pair:{nl}"

    previous_tag_key = None  # Initialize previous tag_key with None
    for (tag_key, tag_value), count in sorted(tag_counts.items()):
        # Check if the current tag_key is different from the previous one
        if tag_key != previous_tag_key:
            # Add a blank line if it's not the first tag_key
            if previous_tag_key is not None:
                summary_message += f"{nl}"
            previous_tag_key = tag_key  # Update the previous tag_key

        # Append the current tag information
        summary_message += f"{tag_key} - {tag_value}: {count}{nl}"

    message_callback(summary_message)
