import pandas as pd
from pathlib import Path

from common import load_json
from common import create_floor_plans_dict
from common import create_tag_keys_dict
from common import create_access_point_measurements_dict
from common import create_measured_radios_dict
from common import create_notes_dict

from common import create_custom_measured_ap_list

from common import nl

right_align = ['2.4 GHz SSIDs', '2.4 Freq', '5 GHz SSIDs', '5 Freq', '6 GHz SSIDs', '6 Freq']


def adjust_column_widths(df, writer):
    """Adjust column widths in the Excel sheet and apply text wrap to the 'Notes' column."""
    worksheet = writer.sheets['AP List']

    # Create a format for wrapping text
    wrap_format = writer.book.add_format({'text_wrap': True, 'valign': 'top'})
    right_align_format = writer.book.add_format({'text_wrap': True, 'valign': 'top', 'align': 'right'})

    # Create a format for aligning to the top without wrapping
    top_align_format = writer.book.add_format({'valign': 'top'})

    for idx, col in enumerate(df.columns):

        # Check if the current column is one we want to wrap
        if col in right_align:
            max_line_len = df[col].astype(str).apply(lambda x: max(len(line) for line in x.split('\n'))).max()
            column_len = max(max_line_len, len(col)) + 1
            worksheet.set_column(idx, idx, column_len, right_align_format)

        elif col == 'Notes':
            worksheet.set_column(idx, idx, (max(df[col].astype(str).map(len).max(), len(col)) + 1), wrap_format)

        else:
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 1
            worksheet.set_column(idx, idx, column_len, top_align_format)


def format_headers(df, writer):
    """Format header row in the Excel sheet."""
    worksheet = writer.sheets['AP List']
    header_format = writer.book.add_format(
        {'bold': True, 'valign': 'center', 'font_size': 16, 'border': 0})

    for idx, col in enumerate(df.columns):
        # Write the header with custom format
        worksheet.write(0, idx, col, header_format)

    # Freeze the header row and the first column
    worksheet.freeze_panes(1, 1)


def create_surveyed_ap_list(working_directory, project_name, message_callback):
    message_callback(f'Generating surveyed AP list for: {project_name}\n')
    project_dir = Path(working_directory) / project_name

    # Load JSON data
    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    access_points_json = load_json(project_dir, 'accessPoints.json', message_callback)
    access_point_measurements_json = load_json(project_dir, 'accessPointMeasurements.json', message_callback)
    measured_radios_json = load_json(project_dir, 'measuredRadios.json', message_callback)
    tag_keys_json = load_json(project_dir, 'tagKeys.json', message_callback)
    notes_json = load_json(project_dir, 'notes.json', message_callback)

    # Process data
    floor_plans_dict = create_floor_plans_dict(floor_plans_json)
    tag_keys_dict = create_tag_keys_dict(tag_keys_json)
    access_point_measurements_dict = create_access_point_measurements_dict(access_point_measurements_json)
    measured_radios_dict = create_measured_radios_dict(measured_radios_json, access_point_measurements_dict)
    notes_dict = create_notes_dict(notes_json)

    surveyed_ap_list = create_custom_measured_ap_list(access_points_json, floor_plans_dict, tag_keys_dict, measured_radios_dict, notes_dict)

    # Create a pandas dataframe and export to Excel
    df = pd.DataFrame(surveyed_ap_list)
    output_filename = f'{project_dir} - AP List.xlsx'

    try:
        writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='AP List', index=False)
        adjust_column_widths(df, writer)
        format_headers(df, writer)
        writer.close()
        message_callback(f'{nl}"{Path(output_filename).name}" created successfully{nl}{nl}### PROCESS COMPLETE ###')
    except Exception as e:
        print(e)
        message_callback(f'{nl}### ERROR: Unable to create "{output_filename}" ###{nl}file could be open in another application{nl}### PROCESS INCOMPLETE ###')
