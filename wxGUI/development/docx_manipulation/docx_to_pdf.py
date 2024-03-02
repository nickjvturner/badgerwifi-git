#!/usr/bin/env python3

"""
Written by Nick Turner (@nickjvturner@mastodon.social)
This script will find 'the' word doc in the same directory as the script
Create an output directory called 'PDF Output'

Initially created in August 2023
Latest meaningful update: 2023-08-10
"""

from pathlib import Path
from docx2pdf import convert

nl = '\n'


def convert_docx_to_pdf(docx_files, message_callback):
    message_callback(f'.docx conversion process started')

    for docx_path in docx_files:
        docx_path = Path(docx_path).resolve()  # Ensure it's an absolute path

        if not docx_path.is_file():
            message_callback(f"File not found: {docx_path}")
            continue

        output_pdf_path = docx_path.with_suffix('.pdf')

        try:
            convert(str(docx_path), str(output_pdf_path.parent))
            message_callback(f"Converted: {docx_path.name} to PDF")
        except Exception as e:
            message_callback(f"Error converting {docx_path.name}: {e}")
