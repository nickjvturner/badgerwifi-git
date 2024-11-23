#!/usr/bin/env python3

"""
The original, well written script by Francois Verges (@VergesFrancois)
Adapted, modified, mangled by Nick Turner (@nickjvturner)
"""
import wx

from common import load_json
from common import nl

import shutil


def export_ap_images(working_directory, project_name, message_callback):

	project_dir = working_directory / project_name

	# Create directory to hold output directories
	output_dir = working_directory / 'OUTPUT'
	output_dir.mkdir(parents=True, exist_ok=True)

	# Create subdirectory for note images
	ap_images_dir = output_dir / 'AP images'
	ap_images_dir.mkdir(parents=True, exist_ok=True)

	access_points_json = load_json(project_dir, 'accessPoints.json', message_callback)
	notes_json = load_json(project_dir, 'notes.json', message_callback)

	if not notes_json:
		wx.CallAfter(message_callback, f'No notes found in the project{nl}')
		return

	wx.CallAfter(message_callback, f'Extracting AP Images from: {project_name}{nl}')

	image_extraction_counter = []

	# Loop through all the APs in the project
	for ap in access_points_json['accessPoints']:
		image_count = 1

		# Check if the AP has any notes
		if 'noteIds' in ap.keys():

			# Check if the AP is placed on a map
			if 'location' in ap.keys():

				# Determine if there are multiple notes with images for this AP
				image_notes_count = sum(1 for ap_note in ap['noteIds'] for note in notes_json['notes'] if note['id'] == ap_note and len(note['imageIds']) > 0)

				for ap_note in ap['noteIds']:

					# Loop through all the notes stored within the project
					for note in notes_json['notes']:

						# Skip notes that do not contain images
						if len(note['imageIds']) > 0:

							# Check if the note id matches the current AP note id
							if note['id'] == ap_note:

								# Loop through all the images attached to the note
								for image in note['imageIds']:
									source_image_file = 'image-' + image
									source_image_full_path = project_dir / source_image_file

									# Determine the output image name
									if image_notes_count > 1 or len(note['imageIds']) > 1:
										# Add image count starting from 1 if there are multiple images associated with this AP
										ap_image_name = f"{ap['name']}-{image_count}.png"
									else:
										# Only one note with images, so no suffix for the first image
										ap_image_name = f"{ap['name']}.png"

									output_destination = ap_images_dir / ap_image_name

									# Count total number of APs extracted
									image_extraction_counter.append(source_image_file)

									shutil.copy(source_image_full_path, output_destination)
									wx.CallAfter(message_callback, f"{ap_image_name} Image extracted")

									image_count += 1

	wx.CallAfter(message_callback, f'{nl}{len(image_extraction_counter)} images extracted{nl}')
