from pathlib import Path
import json



INPUT_DIRECTORY = Path('/Users/nick/Desktop/DDC')

FLOOR_PLAN_INDEX = {'5cd8973e-cbfa-407b-92b0-36279545d3b6': '5c2b6ee6-f9b0-43fe-9284-37966544685b',
                    '5c2b6ee6-f9b0-43fe-9284-37966544685b': '5cd8973e-cbfa-407b-92b0-36279545d3b6'}


def load_json(project_dir, filename, message_callback):
    """Load JSON data from a file."""
    try:
        with open(project_dir / filename) as json_file:
            return json.load(json_file)
    except IOError as e:
        message_callback(f'{filename} not found, this project probably does not contain this data type')
        print(f"Error loading {filename}: {e}")
        return None


# scan the input directory for all files starting with 'survey' and ending with '.json' using pathlib's rglob method
survey_files = list(INPUT_DIRECTORY.rglob('survey-*.json'))

# print the list of survey files
for survey in survey_files:
    # print(survey)

    # load the json file
    with open(str(survey)) as json_file:
        survey_json = json.load(json_file)

    for floorPlan in survey_json['surveys']:
        if floorPlan.get('noteIds'):
            # print(floorPlan.get('floorPlanId'))
            # print(floorPlan.get('noteIds'))
            # print(floorPlan.get('noteIds')[0])
            if floorPlan.get('floorPlanId') in FLOOR_PLAN_INDEX:

                floorPlan['floorPlanId'] = FLOOR_PLAN_INDEX[floorPlan.get('floorPlanId')]
                print(f"{floorPlan.get('floorPlanId')} changed to {FLOOR_PLAN_INDEX[floorPlan.get('floorPlanId')]}")

    # write the modified json file back to the same location
    with open(str(survey), 'w') as json_file:
        json.dump(survey_json, json_file, indent=2)
