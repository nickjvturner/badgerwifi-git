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

            # check if notes.json exists
            if not os.path.exists(Path(project_name) / 'notes.json'):
                print(f'notes.json not found in {project_name}')
                exit()

            # check if accessPoints.json exists
            if not os.path.exists(Path(project_name) / 'accessPoints.json'):
                print(f'accessPoints.json not found in {project_name}')
                exit()

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

            # Loop through all the APs in the project
            for ap in accessPointsJSON['accessPoints']:
                image_count = 1

                # Check if the AP has any notes
                if 'noteIds' in ap.keys():

                    # Check if the AP is placed on a map
                    if 'location' in ap.keys():

                        # Determine if there are multiple notes with images for this AP
                        image_notes_count = sum(1 for ap_note in ap['noteIds'] for note in notesJSON['notes'] if note['id'] == ap_note and len(note['imageIds']) > 0)

                        for ap_note in ap['noteIds']:

                            # Loop through all the notes stored within the project
                            for note in notesJSON['notes']:

                                # Skip notes that do not contain images
                                if len(note['imageIds']) > 0:

                                    # Check if the note id matches the current AP note id
                                    if note['id'] == ap_note:

                                        # Loop through all the images attached to the note
                                        for image in note['imageIds']:
                                            source_image_file = 'image-' + image
                                            source_image_full_path = Path.cwd() / project_name / source_image_file

                                            # Determine the output image name
                                            if image_notes_count > 1 or len(note['imageIds']) > 1:
                                                # Add image count starting from 1 if there are multiple images associated with this AP
                                                ap_image_name = f"{ap['name']}-{image_count}.png"
                                            else:
                                                # Only one note with images, so no suffix for the first image
                                                ap_image_name = f"{ap['name']}.png"

                                            output_destination = ap_image_export_dir / ap_image_name

                                            # Count total number of APs extracted
                                            image_extraction_counter.append(source_image_file)

                                            shutil.copy(source_image_full_path, output_destination)
                                            print(f"[ {ap['name']} ] Image extracted to: AP_images/{ap_image_name}")

                                            image_count += 1

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
