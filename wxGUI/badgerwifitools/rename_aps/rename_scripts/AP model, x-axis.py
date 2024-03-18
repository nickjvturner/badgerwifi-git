# simple, x-axis.py

from common import model_sort_order

ONE_LINER_DESCRIPTION = 'APs sorted by: floor, model, x-axis value'

SHORT_DESCRIPTION = f"""Intended for simulated APs

Sorts APs by:
    floor name,
    model,
    x-axis value

AP-001, AP-002, AP-003..."""

LONG_DESCRIPTION = f"""Created with Simulated APs as the intended targets...

script loads accessPoints.json
places all APs into a list

sorts the list by:
    floor name,
    model,
    x-axis value

the sorted list is iterated through and a new AP Name is assigned

AP numbering starts at 1, with:
    apSeqNum = 1

AP Naming pattern is defined by:
    new_AP_name = f'AP-{{apSeqNum:03}}'

resulting AP names should look like:
    AP-001, AP-002, AP-003..."""


def sort_logic(access_points_list, floor_plans_dict):
    return sorted(access_points_list,
                  key=lambda i: (floor_plans_dict.get(i['location']['floorPlanId']).get('name'),
                                 model_sort_order.get(i['model'], i['model']),
                                 i['location']['coord']['x']))
