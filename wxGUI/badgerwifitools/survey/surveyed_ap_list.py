import pandas as pd
from pathlib import Path

from common import load_json
from common import create_floor_plans_dict
from common import create_tag_keys_dict
from common import create_access_point_measurements_dict
from common import create_measured_radios_dict
from common import create_notes_dict

from common import nl

channel_bands = ['2.4', '5', '6']


right_align_cols =\
    (
        [f'{band} SSIDs' for band in channel_bands] +
        [f'{band} GHz' for band in channel_bands] +
        [f'{band} Supported Rates' for band in channel_bands]
    )

narrow_fixed_width_cols =\
    (
        [f'{band} Ch Primary' for band in channel_bands] +
        [f'{band} Width' for band in channel_bands] +
        [f'{band} Tx Power' for band in channel_bands] +
        [f'{band} WiFi Band' for band in channel_bands] +
        ['Colour', 'hidden']
    )

wide_fixed_width_cols =\
    (
        [f'{band} Security / Standards' for band in channel_bands] +
        [f'{band} Channel from IEs' for band in channel_bands] +
        ['flagged as My AP', 'manually positioned']
    )


def adjust_column_widths(df, writer):
    """Adjust column widths in the Excel sheet and apply text wrap to the 'Notes' column."""
    worksheet = writer.sheets['AP List']

    # Create column text formatting styles
    left_align_wrap = writer.book.add_format({'text_wrap': True, 'valign': 'top'})
    right_align_wrap = writer.book.add_format({'text_wrap': True, 'valign': 'top', 'align': 'right'})

    # Create a format for aligning to the top without wrapping
    left_align = writer.book.add_format({'valign': 'top'})

    for idx, col in enumerate(df.columns):
        column_len = max(df[col].astype(str).map(len).max(), len(col)) + 1

        # Check if the current column is one we want to wrap
        if col in right_align_cols:
            max_line_len = df[col].astype(str).apply(lambda x: max(len(line) for line in x.split('\n'))).max()
            column_len = max(max_line_len, len(col)) - 1
            worksheet.set_column(idx, idx, column_len, right_align_wrap)

        elif col in narrow_fixed_width_cols:
            column_len = 18
            worksheet.set_column(idx, idx, column_len, right_align_wrap)

        elif col in wide_fixed_width_cols:
            column_len = 30
            worksheet.set_column(idx, idx, column_len, right_align_wrap)

        elif col == 'Notes':
            worksheet.set_column(idx, idx, column_len, left_align_wrap)

        else:
            worksheet.set_column(idx, idx, column_len, left_align)


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


def create_surveyed_ap_list(working_directory, project_name, create_custom_measured_ap_list, message_callback):
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
