#!/usr/bin/env python3

"""
The original, well written script by Francois Verges (@VergesFrancois)
Adapted, modified, mangled by Nick Turner (@nickjvturner)

This script will extract all image notes attached to an AP objects of an
Ekahau project file (.esx)

It will place ALL the pictures into directories based upon the date
the picture was taken within a new directory called AP_images

Script should still work if you have multiple pictures per AP note
Working as of 01-FEB-2023

# extract_AP-images_to_DATE_DIR
## Instructions for Use

Place A **COPY** of your project file into the same directory as the python script.

1. Navigate to the folder in your Terminal
2. Execute the python script
3. It should automatically find the project file (.esx)
4. Hit Enter to proceed
5. New directory 'AP_images' is created
6. You get multiple new directories inside 'AP_images' with the picture taken date
7. Inside each date folder you should see an image file with the filename set to the AP Name
"""

import zipfile
import json
import os
import shutil
import time
from pathlib import Path
from pprint import pprint


def main():
	def create_directory(new_dir):
		if not os.path.exists(new_dir):
			os.mkdir(new_dir)
			return f'Directory {new_dir} Created'
		else:
			return f'Directory {new_dir} already exists'

	nl = '\n'

	# Get current working directory
	print(f'{nl}{Path(__file__).name}')
	print(f'working_directory: {Path.cwd()}{nl}')

	# Get local file with extension .esx
	for file in sorted(Path.cwd().iterdir()):
		# ignore files in directory containing _re-zip
		if file.suffix == '.esx':
			proceed = input(f'Proceed with file: {str(file.name)}? (YES/no)')
			if proceed == 'no':
				exit()

			print(f'{nl}Extracting AP Images from: {file.name}')

			# Define the project name
			project_name = file.stem
			print('project_name:', project_name)

			# Unzip the .esx project file into folder named {project_name}
			with zipfile.ZipFile(file.name, 'r') as zip_ref:
				zip_ref.extractall(project_name)
			print('project successfully unzipped')

			# Load the notes.json file into the notesJSON Dictionary
			with open(Path(project_name) / 'notes.json') as json_file:
				notesJSON = json.load(json_file)
				json_file.close()
			# pprint(floorPlansJSON)

			# Load the accessPoints.json file into the accessPointsJSON dictionary
			with open(Path(project_name) / 'accessPoints.json') as json_file:
				accessPointsJSON = json.load(json_file)
				json_file.close()
			# pprint(accessPointsJSON)
				
			ap_image_export_dir = Path.cwd() / 'AP_images'
			create_directory(ap_image_export_dir)
			
			image_extraction_counter = []
			
			for ap in accessPointsJSON['accessPoints']:
				# print(ap['name'])
				if 'noteIds' in ap.keys():
					if 'location' in ap.keys():
						if 'noteIds' in ap.keys():
							for note in notesJSON['notes']:
								if len(ap['noteIds']) > 0:
									if note['id'] == ap['noteIds'][0] and len(note['imageIds']) > 0:
										image_datetime = note['history']['createdAt']
										image_date = image_datetime[0:10]
										# image_time = image_datetime[11:19]

										image_count = 1
										
										for image in note['imageIds']:
											image = 'image-' + image
											image_full_path = Path.cwd() / project_name / image
											
											if len(note['imageIds']) > 1:
												# there must be more than 1 image, add '-1', '-2', '-3', etc
												ap_image_name = f"{ap['name']}-{str(image_count)}.png"
											else:
												ap_image_name = f"{ap['name']}.png"

											# Create 'date' directory
											ap_image_date_dir = ap_image_export_dir / image_date
											create_directory(ap_image_date_dir)

											# count total number of APs extracted
											image_extraction_counter.append(ap_image_name)
											
											shutil.copy(image_full_path, ap_image_date_dir / ap_image_name)
											print(f"[ {ap['name']} ] Image extracted into {image_date} directory")
											
											image_count += 1
											# print(image_count)

			print(f'{nl}{len(image_extraction_counter)} images extracted{nl}')

			remove_extraction_folder = input(f'Do you wish to keep the temp folder [{project_name}] used to unpack .esx file? (NO/yes)')

			if remove_extraction_folder == 'yes':
				exit()
			else:
				project_dir = Path.cwd() / project_name
				shutil.rmtree(project_dir)
				print(f'Unzipped Project directory removed!')

		
if __name__ == "__main__":
	start_time = time.time()
	main()
	run_time = time.time() - start_time
	print(f'** Time to run: {round(run_time, 2)} seconds **')
