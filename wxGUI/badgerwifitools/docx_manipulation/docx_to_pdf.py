# docx_to_pdf.py

from pathlib import Path

import wx
import threading
from docx2pdf import convert

from common import nl


def convert_docx_to_pdf(docx_files, message_callback):
    """
    Converts a list of DOCX files to PDF format.

    :param docx_files: A list of DOCX file paths to be converted.
    :param message_callback: A callback function for logging messages.
    """
    wx.CallAfter(message_callback, f'{nl}DOCX to PDF conversion process started')
    threads = []  # List to keep track of threads
    for docx_file in docx_files:
        thread = threading.Thread(target=convert_single_docx_to_pdf, args=(docx_file, message_callback))
        thread.start()
        threads.append(thread)  # Add the thread to the list of threads

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    wx.CallAfter(message_callback, f'{nl}### PROCESS COMPLETE ###')


def convert_single_docx_to_pdf(docx_file, message_callback):
    """
    Converts a single DOCX file to PDF in a separate thread.

    :param docx_file: Path to the DOCX file to be converted.
    :param message_callback: A callback function for logging messages.
    """
    docx_path = Path(docx_file).resolve()  # Ensures it's an absolute path
    output_pdf_path = docx_path.with_suffix('.pdf')

    try:
        convert(str(docx_path), str(output_pdf_path.parent))
        wx.CallAfter(message_callback, f'PDF created Successfully: {docx_path.name}{nl}')
    except Exception as e:
        wx.CallAfter(message_callback, f'Error converting {docx_path.name}: {e}')
