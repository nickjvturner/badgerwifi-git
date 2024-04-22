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

import shutil
from pathlib import Path
from datetime import datetime

from common import load_json
from common import nl


def export_note_images(working_directory, project_name, message_callback):
	project_dir = Path(working_directory) / project_name

	# Create directory to hold output directories
	output_dir = working_directory / 'OUTPUT'
	output_dir.mkdir(parents=True, exist_ok=True)

	# Create subdirectory for note images
	note_images_dir = output_dir / 'note images'
	note_images_dir.mkdir(parents=True, exist_ok=True)

	access_points_json = load_json(project_dir, 'accessPoints.json', message_callback)
	notes_json = load_json(project_dir, 'notes.json', message_callback)

	if not notes_json:
		message_callback(f'No notes found in the project{nl}')
		return

	# Create a list of all noteIds that are associated with an AP
	ap_note_ids = []
	for ap in access_points_json['accessPoints']:
		if 'noteIds' in ap.keys() and len(ap['noteIds']) > 0:
			ap_note_ids.append(ap['noteIds'][0])

	message_callback(f'Extracting Images from: {project_name} notes')

	image_extraction_counter = []

	for note in notes_json['notes']:
		if note['id'] not in ap_note_ids:
			if len(note['imageIds']) > 0:
				image_count = 1

				for image in note['imageIds']:
					image = 'image-' + image
					image_full_path = project_dir / image

					# Process the createdAt stamp to make it filename friendly
					created_at = datetime.fromisoformat((note['history']['createdAt']).replace('Z', '+00:00')).strftime(f"%Y-%m-%d__%H-%M-%S")

					if len(note['imageIds']) > 1:
						# there must be more than 1 image, add '-1', '-2', '-3', etc
						note_image_name = f"{created_at}-{str(image_count)}.png"
					else:
						note_image_name = f"{created_at}.png"

					dst = note_images_dir / note_image_name

					# count total number of APs extracted
					image_extraction_counter.append(note_image_name)

					shutil.copy(image_full_path, dst)
					message_callback(f"{image} extracted as {note_image_name}")

					image_count += 1

	message_callback(f'{nl}{len(image_extraction_counter)} images extracted{nl}')
