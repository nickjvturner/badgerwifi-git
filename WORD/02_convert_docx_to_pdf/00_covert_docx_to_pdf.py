#!/usr/bin/env python3

"""
Written by Nick Turner (@nickjvturner)
This script will find 'the' word doc in the same directory as the script
Create an output directory called 'PDF Output'

Initially created in August 2023
Latest meaningful update: 2023-08-10
"""

from pathlib import Path

nl = '\n'

try:
    from docx2pdf import convert
except ImportError as e:
	print(f'{e}{nl}try installing docx2pdf module{nl}"pip install docx2pdf"')

def main():
	docx_files = []

	# Get local file with extension .docx
	for file in sorted(Path.cwd().iterdir()):
		# ignore docx files in directory with $ and OUTPUT in filename
		if file.suffix == '.docx' and all(char not in file.stem for char in ('$', 'OUTPUT')):
			docx_files.append(file)

	for docx in docx_files:
		print(docx.name)
	proceed = input(f'{nl}Proceed with listed files?: (YES/no)')
	if proceed.lower() == 'no':
		exit()

	# print(f'{nl}filename: {file.name}')

	for docx in docx_files:
		print(f'{nl}{docx.name}')
		output_pdf_file = docx.stem + ".pdf"

		convert(docx.name, output_pdf_file)

if __name__ == "__main__":
	main()
