# generate_bom_xlsx.py

import json
import pandas as pd
from pathlib import Path
from common import ekahau_color_dict
from common import load_json
from common import create_floor_plans_dict
from common import create_tag_keys_dict
from common import create_simulated_radios_dict
from common import create_custom_AP_list
from common import create_notes_dict

# Constants
VERSION = '1.2'

def generate_bom(working_directory, project_name, message_callback):
    message_callback(f'Generation BoM XLSX for: {project_name}\n')
    project_dir = Path(working_directory) / project_name

    # Load JSON data
    floorPlansJSON = load_json(project_dir, 'floorPlans.json')
    accessPointsJSON = load_json(project_dir, 'accessPoints.json')
    simulatedRadiosJSON = load_json(project_dir, 'simulatedRadios.json')
    tagKeysJSON = load_json(project_dir, 'tagKeys.json')
    notesJSON = load_json(project_dir, 'notes.json')


    # Process data
    floorPlansDict = create_floor_plans_dict(floorPlansJSON)
    tagKeysDict = create_tag_keys_dict(tagKeysJSON)
    simulatedRadioDict = create_simulated_radios_dict(simulatedRadiosJSON)
    notesDict = create_notes_dict(notesJSON)
    custom_AP_list = create_custom_AP_list(accessPointsJSON, floorPlansDict, tagKeysDict, simulatedRadioDict, notesDict)

    # Create a pandas dataframe and export to Excel
    df = pd.DataFrame(custom_AP_list)
    output_filename = f'{project_dir} - BoM v{VERSION}.xlsx'
    writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='AP List', index=False)
    adjust_column_widths(df, writer)
    format_headers(df, writer)
    writer.save()
    message_callback(f'BoM XLSX generated: {output_filename}\n')

def adjust_column_widths(df, writer):
    """Adjust column widths in the Excel sheet."""
    worksheet = writer.sheets['AP List']
    for idx, col in enumerate(df.columns):
        column_len = max(df[col].astype(str).map(len).max(), len(col)) + 5
        worksheet.set_column(idx, idx, column_len * 1.2)


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

