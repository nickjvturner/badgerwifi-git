#!/usr/bin/env python3

"""
Created by Nick Turner
nickjvturner.com
@nickjvturner
@nickjvturner@mastodon.social

This script finds local directories and re-packs them into a *hopefully* functional .esx project file

"""

import shutil
from pathlib import Path

nl = '\nl'

# Get current working directory
print(f'{nl}{Path(__file__).name}')
print(f'working_directory: {Path.cwd()}{nl}')

# Get local directory (hopefully there is only 1x)
for dir in sorted(Path.cwd().iterdir()):
	# ignore files in directory containing _re-zip
	if dir.is_dir():
		proceed = input(f'Proceed to rebundle this directory: {str(dir.name)}? (YES/no)')
		if proceed == 'no':
			continue

		print(f'directory name: {dir.name}{nl}')

		new_file_name = dir.name + '_re-zip'
		new_file_name_zip = new_file_name + '.zip'
		new_file_name_esx = new_file_name + '.esx'

		try:
			shutil.make_archive(new_file_name, 'zip', dir)
			shutil.move(new_file_name_zip, new_file_name_esx)
			print(f'''Process complete
			'{new_file_name_esx}' successfully re-bundled into .esx file''')
		except Exception as e:
			print(e)
