# rename_aps_IK.py

import json
from pathlib import Path
import shutil

nl = '\n'

def rename_aps(working_directory, project_name, message_callback):
    message_callback(f'Performing action for: {project_name}')

    try:
        with open(working_directory / project_name / 'floorPlans.json') as json_file:
            floorPlansJSON = json.load(json_file)

        floorPlansDict = {floor['id']: floor['name'] for floor in floorPlansJSON['floorPlans']}

        with open(working_directory / project_name / 'accessPoints.json') as json_file:
            accessPointsJSON = json.load(json_file)

        accessPointsLIST = [ap for ap in accessPointsJSON['accessPoints']]

        def floorPlanGetter(floorPlanId):
            return floorPlansDict.get(floorPlanId)

        accessPointsLIST_SORTED = sorted(accessPointsLIST,
                                         key=lambda i: (floorPlanGetter(i['location']['floorPlanId']),
                                                        i['model'],
                                                        i['location']['coord']['x']))
    except KeyError as e:
        message_callback(f"Error: {str(e)} - Project file contains 'surveyed' APs with no x,y coordinates.")
        return

    apSeqNum = 1
    for ap in accessPointsLIST_SORTED:
        new_AP_name = f'AP-{apSeqNum:03}'
        message_callback(f"[[ {ap['name']} [{ap['model']}]] from: {floorPlanGetter(ap['location']['floorPlanId'])} ] renamed to {new_AP_name}")
        ap['name'] = new_AP_name
        apSeqNum += 1

    sorted_accessPointsJSON_dict = {'accessPoints': accessPointsLIST_SORTED}

    try:
        print(project_name)
        with open("accessPoints.json", "w") as outfile:
            json.dump(sorted_accessPointsJSON_dict, outfile, indent=4)
        shutil.move('accessPoints.json', working_directory / project_name / 'accessPoints.json')

        output_esx = project_name + '_re-zip'
        output_esx_path = working_directory / output_esx

        shutil.make_archive(str(output_esx_path), 'zip', str(working_directory / project_name))
        shutil.move(str(output_esx_path) + '.zip', str(output_esx_path) + '.esx')  # Using string concatenation in preference to '.withsuffix' due to issues with periods in project names
        message_callback(f'{nl}Process complete {nl}{output_esx} re-bundled into .esx file')
    except Exception as e:
        message_callback(f"An error occurred: {str(e)}")
