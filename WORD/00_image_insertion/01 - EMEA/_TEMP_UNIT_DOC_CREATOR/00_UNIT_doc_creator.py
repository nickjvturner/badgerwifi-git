#!/usr/bin/env python3

"""
Written by Nick Turner (@nickjvturner)
This script will find 'the' word doc in the same directory as the script
iterate through all the table cells and replace text strings with
specified replacement strings.

Created December 2022 in response to a throw-away comment by Jerry Olla @jolla
"""

from pathlib import Path
from docx import Document
import time


def main():
	# Get local file with extension .docx
	for file in sorted(Path.cwd().iterdir()):
		# ignore files in directory containing output
		if (file.suffix == '.docx') and (not ('output' in file.stem)):
			proceed = input(f'Proceed with file: {str(file.name)}? (YES/no)')
			if proceed == 'no':
				exit()

			print('filename:', file.name)

			unit_list = ['MPS', 'OG2', 'OH', 'OL4', 'OM4', 'OM6', 'ONC', 'OP-K', 'OT3', 'OT4', 'OUP', 'OUW', 'SCW']

			search_key = '*UNIT*'

			for unit in unit_list:

				document = Document(file)

				for paragraph in document.paragraphs:
					if search_key in paragraph.text:
						paragraph.text = paragraph.text.replace(search_key, unit)
						print(search_key, 'text replaced with', unit)

				document.save(Path.cwd() / Path(file.stem + '-' + unit + '.docx'))


if __name__ == "__main__":
	start_time = time.time()
	main()
	run_time = time.time() - start_time
	print(f'** Time to run: {round(run_time, 2)} seconds **')

