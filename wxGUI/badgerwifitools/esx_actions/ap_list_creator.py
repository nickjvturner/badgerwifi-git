# project_IK.py

import pandas as pd
from pathlib import Path

from common import load_json
from common import create_floor_plans_dict
from common import create_tag_keys_dict
from common import create_simulated_radios_dict
from common import create_notes_dict

nl = '\n'


def adjust_column_widths(df, writer):
    """Adjust column widths in the Excel sheet and apply text wrap to the 'Notes' column."""
    worksheet = writer.sheets['AP List']
    # Create a format for wrapping text
    wrap_format = writer.book.add_format({'text_wrap': True})

    for idx, col in enumerate(df.columns):
        column_len = max(df[col].astype(str).map(len).max(), len(col)) + 5
        # Check if the current column is 'Notes' to apply text wrap format
        if col == 'Notes':
            worksheet.set_column(idx, idx, column_len * 1.2, wrap_format)
        else:
            worksheet.set_column(idx, idx, column_len * 1.2)


def format_headers(df, writer):
    """Format header row in the Excel sheet."""
    worksheet = writer.sheets['AP List']
    header_format = writer.book.add_format(
        {'bold': True, 'valign': 'center', 'font_size': 16, 'border': 0})

    for idx, col in enumerate(df.columns):
        # Write the header with custom format
        worksheet.write(0, idx, col, header_format)


def create_ap_list(working_directory, project_name, message_callback, create_custom_ap_list):
    message_callback(f'Generating BoM XLSX for: {project_name}\n')
    project_dir = Path(working_directory) / project_name

    # Load JSON data
    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    access_points_json = load_json(project_dir, 'accessPoints.json', message_callback)
    simulated_radios_json = load_json(project_dir, 'simulatedRadios.json', message_callback)
    tag_keys_json = load_json(project_dir, 'tagKeys.json', message_callback)
    notes_json = load_json(project_dir, 'notes.json', message_callback)

    # Process data
    floor_plans_dict = create_floor_plans_dict(floor_plans_json)
    tag_keys_dict = create_tag_keys_dict(tag_keys_json)
    simulated_radio_dict = create_simulated_radios_dict(simulated_radios_json)
    notes_dict = create_notes_dict(notes_json)

    custom_ap_list = create_custom_ap_list(access_points_json, floor_plans_dict, tag_keys_dict, simulated_radio_dict, notes_dict)

    # Create a pandas dataframe and export to Excel
    df = pd.DataFrame(custom_ap_list)
    output_filename = f'{project_dir} - AP List.xlsx'

    writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='AP List', index=False)
    adjust_column_widths(df, writer)
    format_headers(df, writer)
    writer.close()
    message_callback(f'{nl}"{Path(output_filename).name}" created successfully{nl}{nl}### PROCESS COMPLETE ###')
