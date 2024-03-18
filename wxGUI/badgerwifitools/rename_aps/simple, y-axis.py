# simple, y-axis.py

ONE_LINER_DESCRIPTION = 'APs sorted by: floor, y-axis value'

SHORT_DESCRIPTION = f"""Intended for simulated APs
Re-sorts APs by:
    floor name,
    y-axis value
    
AP-001, AP-002, AP-003..."""

LONG_DESCRIPTION = f"""Created with [SIMULATED APs] as the targets...

script loads accessPoints.json
places all APs into a list

sorts the list by:
    floor name
    y-axis value

the sorted list is iterated through and a new AP Name is assigned

AP Naming pattern is defined by:
    new_AP_name = f'AP-{{apSeqNum:03}}'
    
resulting AP names should look like:
    AP-001, AP-002, AP-003..."""


def sort_logic(access_points_list, floor_plans_dict):
    return sorted(access_points_list, key=lambda i: (floor_plans_dict.get(i['location']['floorPlanId']).get('name'),
                                                     i['location']['coord']['y']))
