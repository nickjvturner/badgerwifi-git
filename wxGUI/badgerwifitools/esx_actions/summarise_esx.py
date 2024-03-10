# summarise_esx_.py

from collections import defaultdict

from common import load_json
from common import create_floor_plans_dict
from common import create_tag_keys_dict
from common import create_simulated_radios_dict
from common import create_custom_ap_dict
from common import ekahau_color_dict

# CONSTANTS
nl = '\n'


def summarise_esx(working_directory, project_name, message_callback):
    message_callback(f'Summarising the Contents of: {project_name}')

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
    custom_ap_dict = create_custom_ap_dict(access_points_json, floor_plans_dict, simulated_radio_dict)

    for ap in access_points_json['accessPoints']:
        for tag in ap['tags']:
            custom_ap_dict[ap['name']]['tags'][tag_keys_dict.get(tag['tagKeyId'])] = tag['value']

    # Initialize defaultdict to count attributes
    color_counts = defaultdict(int)
    antenna_height_counts = defaultdict(int)

    tag_counts = defaultdict(int)

    model_counts = defaultdict(int)

    # Count occurrences of each
    for ap in custom_ap_dict.values():

        color_counts[ap['color']] += 1

        antenna_height_counts[ap['antennaHeight']] += 1

        # Iterate through the tags dictionary within each AP
        for tag_key, tag_value in ap['tags'].items():
            tag_counts[(tag_key, tag_value)] += 1

        model_counts[ap['model']] += 1

    # Prepare the summary message
    summary_message = f"{nl}Count of each model type:{nl}"
    for model, count in sorted(model_counts.items()):
        summary_message += f"{model}: {count}{nl}"

    summary_message += f"{nl}Count of each color:{nl}"
    color_counts_sorted = sorted(color_counts.items(), key=lambda item: ekahau_color_dict.get(item[0], item[0]))
    for color, count in color_counts_sorted:
        summary_message += f"{ekahau_color_dict.get(color)}: {count}{nl}"

    summary_message += f"{nl}Count of each AP height:{nl}"
    for height, count in sorted(antenna_height_counts.items()):
        summary_message += f"{height}: {count}{nl}"

    if tag_keys_json is not None:
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
