#!/usr/bin/env python3

"""
Written by Nick Turner (@nickjvturner@mastodon.social)
This script will find 'the' word doc in the same directory as the script
Create an output directory called 'PDF Output'

Initially created in August 2023
Latest meaningful update: 2023-08-10
"""

from pathlib import Path

import wx
from docx2pdf import convert
import threading

nl = '\n'


def convert_docx_to_pdf_threaded(docx_file, message_callback):
    # Wrapper function to run convert_docx_to_pdf in a separate thread
    def run_in_thread():
        convert_docx_to_pdf(docx_file, message_callback)

    # Start the long-running task in a separate thread
    threading.Thread(target=run_in_thread).start()


def convert_docx_to_pdf(docx_file, message_callback):
    wx.CallAfter(message_callback, '.docx conversion process started')

    docx_path = Path(docx_file).resolve()  # Ensure it's an absolute path

    output_pdf_path = docx_path.with_suffix('.pdf')

    try:
        convert(str(docx_path), str(output_pdf_path.parent))
        message_callback(f"Converted: {docx_path.name} to PDF")
    except Exception as e:
        message_callback(f"Error converting {docx_path.name}: {e}")
