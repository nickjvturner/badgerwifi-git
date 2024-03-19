# Fuzzy y-axis.py

from common import model_sort_order

SPLIT_BOUNDARY_GROUPS = True  # flag attribute
BOUNDARY_SEPARATOR = True  # flag attribute
BOUNDARY_ORIENTATION = 'vertical'  # flag attribute

ONE_LINER_DESCRIPTION = 'APs sorted by: floor, model, x-axis in columns, y-axis value'

SHORT_DESCRIPTION = f"""Intended for simulated APs

Sorts APs by:
    floor name,
    model,
    x-axis in 'columns',
    y-axis value

AP-001, AP-002, AP-003..."""

LONG_DESCRIPTION = f"""This renaming function works by:
placing all project APs into a list

initially sorting the list by:
    floor name,
    x-axis value

the APs are then iterated through and assigned to a group
based on their x-axis value
the first AP in the list defines the start of the first group
subsequent APs with an x-axis value within the threshold
are also assigned to the first group
when an AP with an x-axis value greater than the threshold is found
a new group is started
the assessment of APs continues
eventually all APs are assigned to a group
    
the list is re-sorted by:
    floor name,
    model,
    x-axis in 'columns',
    y-axis value
    
the sorted list is iterated through and a new AP Name is assigned
AP numbering starts at 1, with:

resulting AP names will look like:
    AP-001, AP-002, AP-003...
"""


def sort_logic(access_points_list, floor_plans_dict, x_axis_threshold, output_boundaries=False):
    # First, sort APs by floor name (via floorPlanId) and then by y-coordinate.
    access_points_list_sorted = sorted(access_points_list,
                                       key=lambda ap: (
                                        floor_plans_dict.get(ap['location']['floorPlanId']).get('name', ''),
                                        ap['location']['coord']['x']))

    # Initialize variables for grouping.
    x_coordinate_group = 1
    current_group_start_x = None
    boundaries = []

    for ap in access_points_list_sorted:
        if current_group_start_x is None:
            # First AP in the list defines the start of the first group.
            current_group_start_x = ap['location']['coord']['x']
            boundaries.append(current_group_start_x)
        elif (ap['location']['coord']['x'] - current_group_start_x) > x_axis_threshold:
            # Current AP's x-coordinate is outside the threshold of the current group; start a new group.
            x_coordinate_group += 1
            current_group_start_x += x_axis_threshold
            boundaries.append(current_group_start_x)

        # Assign group ID to the AP.
        ap['location']['coord']['x_group'] = x_coordinate_group

    # After grouping, you can further sort APs within each group if needed.
    # For example, by x-coordinate or another attribute.

    # Final sorting by group ID, then y-coordinate within each group.
    access_points_list_sorted = sorted(access_points_list_sorted,
                                       key=lambda i: (floor_plans_dict.get(i['location']['floorPlanId']).get('name'),
                                                      model_sort_order.get(i['model'], i['model']),
                                                      i['location']['coord']['x_group'],
                                                      i['location']['coord']['y']))

    if output_boundaries:
        # Calculate the center for the last group.
        return access_points_list_sorted, boundaries, BOUNDARY_ORIENTATION

    return access_points_list_sorted
