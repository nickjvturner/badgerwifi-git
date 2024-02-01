#!/usr/bin/env python3

"""
Created by Nick Turner
nickjvturner.com
@nickjvturner
@nickjvturner@mastodon.social

This script finds local .esx files and unpacks them into a new local directory

"""

import zipfile
from pathlib import Path

nl = '\n'

# Get current working directory
print(f'{nl}{Path(__file__).name}')
print(f'working_directory: {Path.cwd()}{nl}')

# Get local file with extension .esx
for file in sorted(Path.cwd().iterdir()):
	# ignore files in directory containing _re-zip
	if (file.suffix == '.esx') and (not ('re-zip' in file.stem)):
		proceed = input(f'Proceed with file: {str(file.name)}? (YES/no)')
		if proceed == 'no':
			continue

		print('filename:', file.name)

		# Define the project name
		project_name = file.stem
		print('project_name:', project_name)

		# Unzip the .esx project file into folder named {project_name}
		with zipfile.ZipFile(file.name, 'r') as zip_ref:
			zip_ref.extractall(project_name)
		print('project successfully unzipped')
