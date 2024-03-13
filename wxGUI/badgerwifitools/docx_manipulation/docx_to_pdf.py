# docx_to_pdf.py

from pathlib import Path

import wx
import threading
from docx2pdf import convert

from common import nl


def convert_docx_to_pdf_threaded(docx_file, message_callback):
    # Wrapper function to run convert_docx_to_pdf in a separate thread
    def run_in_thread():
        convert_docx_to_pdf(docx_file, message_callback)

    # Start the long-running task in a separate thread
    threading.Thread(target=run_in_thread).start()


def convert_docx_to_pdf(docx_file, message_callback):
    wx.CallAfter(message_callback, f'{nl}DOCX to PDF conversion process started')

    docx_path = Path(docx_file).resolve()  # Ensure it's an absolute path

    output_pdf_path = docx_path.with_suffix('.pdf')

    try:
        convert(str(docx_path), str(output_pdf_path.parent))
        message_callback(f'PDF created Successfully: {docx_path.name}{nl}{nl}### PROCESS COMPLETE ###')
    except Exception as e:
        message_callback(f'Error converting {docx_path.name}: {e}')
