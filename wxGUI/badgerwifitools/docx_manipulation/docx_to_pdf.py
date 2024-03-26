# docx_to_pdf.py

from pathlib import Path

import wx
import threading
from docx2pdf import convert

from common import nl


def convert_docx_to_pdf(docx_files, message_callback):
    """
    Converts a list of DOCX files to PDF format.
    """
    # Wrapper function to run process in a separate thread
    def run_in_thread():
        convert_single_docx_to_pdf(docx_files, message_callback)

    wx.CallAfter(message_callback, f'{nl}DOCX to PDF conversion process started')

    # Start the long-running task in a separate thread
    threading.Thread(target=run_in_thread).start()


def convert_single_docx_to_pdf(docx_files, message_callback):
    """
    Converts DOCX files to PDF in a separate thread.
    """

    for docx_file in docx_files:
        docx_path = Path(docx_file).resolve()  # Ensures it's an absolute path
        output_pdf_path = docx_path.with_suffix('.pdf')

        working_directory = docx_path.parent

        # Create directory to hold output directories
        output_dir = working_directory / 'OUTPUT'
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            convert(str(docx_path), str(output_dir))
            wx.CallAfter(message_callback, f'PDF created Successfully: {docx_path.name}{nl}')
        except Exception as e:
            wx.CallAfter(message_callback, f'Error converting {docx_path.name}: {e}')
