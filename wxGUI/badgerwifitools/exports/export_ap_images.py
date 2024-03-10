#!/usr/bin/env python3

"""
The original, well written script by Francois Verges (@VergesFrancois)
Adapted, modified, mangled by Nick Turner (@nickjvturner)

This script will extract all image notes attached to an AP objects of an
Ekahau project file (.esx)

It will place ALL the pictures into a single, new directory called AP_images

Script should still work if you have multiple pictures per AP note
Working as of 01-FEB-2023
"""

from common import load_json
import shutil

nl = '\n'


def export_ap_images(working_directory, project_name, message_callback):

	project_dir = working_directory / project_name

	# Create a backup folder if it doesn't exist
	ap_image_dir = working_directory / "AP Images"
	ap_image_dir.mkdir(parents=True, exist_ok=True)

	access_points_json = load_json(project_dir, 'accessPoints.json', message_callback)
	notes_json = load_json(project_dir, 'notes.json', message_callback)

	if not notes_json:
		message_callback(f'No notes found in the project{nl}')
		return

	message_callback(f'Extracting AP Images from: {project_name}')

	image_extraction_counter = []

	for ap in access_points_json['accessPoints']:
		if 'noteIds' in ap.keys():
			if 'location' in ap.keys():
				if 'noteIds' in ap.keys():
					for note in notes_json['notes']:
						if len(ap['noteIds']) > 0:
							if note['id'] == ap['noteIds'][0] and len(note['imageIds']) > 0:
								image_count = 1

								for image in note['imageIds']:
									image = 'image-' + image
									image_full_path = project_dir / image

									if len(note['imageIds']) > 1:
										# there must be more than 1 image, add '-1', '-2', '-3', etc
										ap_image_name = f"{ap['name']}-{str(image_count)}.png"
									else:
										ap_image_name = f"{ap['name']}.png"

									dst = ap_image_dir / ap_image_name

									# count total number of APs extracted
									image_extraction_counter.append(ap_image_name)

									shutil.copy(image_full_path, dst)
									message_callback(f"{ap['name']} Image extracted")

									image_count += 1

	message_callback(f'{nl}{len(image_extraction_counter)} images extracted{nl}')
