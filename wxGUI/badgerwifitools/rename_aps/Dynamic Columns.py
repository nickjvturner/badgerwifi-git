# Fuzzy y-axis.py

from common import model_sort_order

dynamic_widget = 'flag attribute'
visualise_centre_rows = 'flag attribute'

ONE_LINER_DESCRIPTION = 'APs sorted by: floor, model, y-axis in columns, x-axis value'

SHORT_DESCRIPTION = f"""Intended for simulated APs

Sorts APs by:
    floor name,
    model,
    y-axis in 'bands',
    x-axis value

AP-001, AP-002, AP-003..."""

LONG_DESCRIPTION = f"""Created with [SIMULATED APs] as the targets...

script loads accessPoints.json
places all APs into a list

sorts the list by:
    floor name,
    model,
    y-axis in 'bands',
    x-axis value

the sorted list is iterated through and a new AP Name is assigned

AP Naming pattern is defined by:
    AP-{{apSeqNum:03}}
    
The resulting AP numbering looks like:
    AP-001, AP-002, AP-003...

per floor
script places all APs into a list
sorts the list by the y-axis value
iterates through the sorted list
the very first AP is assigned to y_coordinate_group 1
establish a value for the acceptable_deviation within the y-axis
    value is calculated by dividing the current map image height by the vertical_division_factor
    one twentieth of the current map image height
    I invite you to manually edit this value, if you so wish
subsequent APs with a y-axis value within the acceptable_deviation will also be assigned to y_coordinate_group 1
when an AP with a y-axis value greater than the acceptable_deviation is found, the y_coordinate_group id is incremented
the assessment of APs continues
eventually all APs are assigned a y_coordinate_group id
the list is re-sorted by:
    y_group, x-axis value
    specifically in this order
having been grouped into '20' (horizontal) rows
the APs are now sorted by their x-axis value within each row
the sorted list is iterated through and a new AP Name is assigned"""


def sort_logic(access_points_list, floor_plans_dict, x_axis_threshold, output_boundaries=False):
    # First, sort APs by floor name (via floorPlanId) and then by y-coordinate.
    access_points_list_sorted = sorted(access_points_list, key=lambda ap: (
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
        return access_points_list_sorted, boundaries, 'vertical'

    return access_points_list_sorted
