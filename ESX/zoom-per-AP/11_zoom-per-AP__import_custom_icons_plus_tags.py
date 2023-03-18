#!/usr/bin/env python3

"""
Created by Nick Turner (@nickjvturner)


"""

import os
import zipfile
import json
import shutil
import time
import platform
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from pprint import pprint


def main():
    def create_directory(new_dir):
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
            return f'Directory {new_dir} Created'
        else:
            return f'Directory {new_dir} already exists'


    def text_width_and_height_getter(text):
        # Create a working space image and draw object
        working_space = Image.new("RGB", (500, 500), color="white")
        draw = ImageDraw.Draw(working_space)

        # Draw the text onto the image and get its bounding box
        text_box = draw.textbbox((0, 0), text, font=font, spacing=4, align="center")

        # Print the width and height of the bounding box
        width = text_box[2] - text_box[0]
        height = text_box[3] - text_box[1]

        return width, height

    nl = '\n'

    # Get filename and current working directory
    print(f'{nl}{Path(__file__).name}')
    print(f'working_directory: {Path.cwd()}{nl}')

    # Get local file with extension .esx
    for file in sorted(Path.cwd().iterdir()):
        # ignore files in directory containing _re-zip
        if (file.suffix == '.esx') and (not('re-zip' in file.stem)):
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

            # Load the floorPlans.json file into the floorPlansJSON Dictionary
            with open(Path(project_name) / 'floorPlans.json') as json_file:
                floorPlans = json.load(json_file)
            # pprint(floorPlans)

            # Create an intermediary dictionary to lookup floor names
            floorPlansDict = {}

            # Populate the intermediary dictionary with {floorId: floor name}
            for floor in floorPlans['floorPlans']:
                floorPlansDict[floor['id']] = floor['name']
            # pprint(floorPlansDict)

            def floorPlanGetter(floorPlanId):
                # print(floorPlansDict.get(floorPlanId))
                return floorPlansDict.get(floorPlanId)

            try:
                # Load the notes.json file into the notes dictionary
                with open(Path(project_name) / 'notes.json') as json_file:
                    notes = json.load(json_file)
                # pprint(notes)

                # Create an intermediary dictionary to lookup simulated radio parameters
                notesDict = {}

                # Populate the intermediary dictionary
                for note in notes['notes']:
                    notesDict[note['id']] = {}  # initialize nested dictionary
                    for x, y in note.items():
                        # print(x, y)
                        notesDict[note['id']][x] = y
            except Exception as e:
                print(f'notes.json not found inside project file, this probably means that there are not any APs with notes')

            # pprint(notesDict)

            try:
                # Load the tagKey.json file into the notes dictionary
                with open(Path(project_name) / 'tagKeys.json') as json_file:
                    tagKeys = json.load(json_file)
                # pprint(tagKeys)

                # Create an intermediary dictionary to lookup simulated radio parameters
                tagKeyDict = {}

                # Populate the intermediary dictionary
                for tagKey in tagKeys['tagKeys']:
                    # print(tagKey)
                    tagKeyDict[tagKey['id']] = {}  # initialize nested dictionary
                    for x, y in tagKey.items():
                        # print(x, y)
                        tagKeyDict[tagKey['id']][x] = y
            except Exception as e:
                print(f'tagKeys.json not found inside project file, this probably means that there are no APs with tags')

            # pprint(tagKeyDict)


            # Load the simulatedRadios.json file into the simulatedRadios dictionary
            with open(Path(project_name) / 'simulatedRadios.json') as json_file:
                simulatedRadios = json.load(json_file)
            # pprint(simulatedRadios)

            # Create an intermediary dictionary to lookup simulated radio parameters
            simulatedRadioDict = {}

            # Populate the intermediary dictionary
            for radio in simulatedRadios['simulatedRadios']:
                simulatedRadioDict[radio['accessPointId']] = {}  # initialize nested dictionary
                for x, y in radio.items():
                    # print(x, y)
                    simulatedRadioDict[radio['accessPointId']][x] = y

            # pprint(simulatedRadioDict)
            # print(simulatedRadioDict['84d58cfc-1121-4b8c-97e7-c589f56494e4']['antennaHeight'])

            # Load the accessPoints.json file into the accessPoints dictionary
            with open(Path(project_name) / 'accessPoints.json') as json_file:
                accessPoints = json.load(json_file)
            # pprint(accessPoints)

            # Create directory to hold output directories
            create_directory(Path.cwd() / 'OUTPUT')

            # Create subdirectory for Blank floor plans
            plain_floorplan_destination = Path.cwd() / 'OUTPUT' / 'blank'
            create_directory(plain_floorplan_destination)

            # Create subdirectory for 'zoomed isolated AP' images
            zoomed_AP_destination = Path.cwd() / 'OUTPUT' / 'zoomed-APs'
            create_directory(zoomed_AP_destination)

            # Create subdirectory for Annotated floorplans
            annotated_floorplan_destination = Path.cwd() / 'OUTPUT' / 'annotated'
            create_directory(annotated_floorplan_destination)

            # Import custom icons
            arrow = Image.open('arrow.png')
            spot = Image.open('spot.png')

            # Resize icons if necessary (default size is 350x350 px)
            icon_resize = 200

            arrow = arrow.resize((icon_resize, icon_resize))
            spot = spot.resize((icon_resize, icon_resize))

            # Define the centre point of the icon
            arrow_centre_point = (arrow.width // 2, arrow.height // 2)

            # PIL Parameters
            crop_size = 1200
            offset = 15

            # Define text, font and size
            if platform.system() == "Windows":
                font_path = os.path.join(os.environ["SystemRoot"], "Fonts", "Consola.ttf")
                font = ImageFont.truetype(font_path, 30)
            else:
                font = ImageFont.truetype("Menlo.ttc", 30)

            for floor in floorPlans['floorPlans']:
                # Extract floorplans
                shutil.copy((Path(project_name) / ('image-' + floor['imageId'])), Path(plain_floorplan_destination / floor['name']).with_suffix('.png'))
                shutil.copy((Path(project_name) / ('image-' + floor['imageId'])), floor['imageId'])

                # Open the floorplan to be used for all AP placement
                all_APs = Image.open(floor['imageId'])

                # Create an ImageDraw object
                draw_all_APs = ImageDraw.Draw(all_APs)

                for ap in sorted(accessPoints['accessPoints'], key=lambda i: i['name']):
                    # print(ap)
                    # print(ap['location']['floorPlanId'])

                    if ap['location']['floorPlanId'] == floor['id']:

                        # establish x and y
                        x, y = (ap['location']['coord']['x'], ap['location']['coord']['y'])

                        print(
                            f"{nl}[[ {ap['name']} [{ap['model']}]] from: {floorPlanGetter(ap['location']['floorPlanId'])} ] "
                            f"has coordinates {x}, {y}")

                        # Open the floorplan to be used for isolated AP image
                        isolated_AP = Image.open(floor['imageId'])

                        # Create ImageDraw object
                        draw_isolated_AP = ImageDraw.Draw(isolated_AP)

                        angle = simulatedRadioDict[ap['id']]['antennaDirection']
                        print(f'AP has rotational angle of: {angle}')

                        antennaTilt = simulatedRadioDict[ap['id']]['antennaTilt']
                        antennaMounting = simulatedRadioDict[ap['id']]['antennaMounting']
                        antennaHeight = simulatedRadioDict[ap['id']]['antennaHeight']

                        try:
                            ap_notes = []
                            for noteId in ap['noteIds']:
                                ap_notes.append(notesDict[noteId]['text'])
                            ap_note = '\n'.join(ap_notes)
                        except KeyError:
                            ap_note = ''

                        try:
                            ap_tags = []
                            for tag in ap['tags']:
                                # print(tag)
                                ap_tagKeyId = tag['tagKeyId']
                                # print(tagKeyDict[ap_tagKeyId]['key'])
                                ap_tag = tagKeyDict[ap_tagKeyId]['key']
                                ap_tag_value = tag['value']
                                # print(ap_tag)
                                ap_tags.append(f"{ap_tag}: {ap_tag_value}")
                            ap_tags = '\n'.join(ap_tags)
                            print(ap_tags)
                        except KeyError:
                            ap_note = ''

                        plans = (all_APs, isolated_AP)

                        # Offset the text below the AP icon
                        y_offsetter = arrow.height / 2.5

                        if angle != 0.0:
                            rotated_arrow = arrow.rotate(angle, expand=True)

                            # Define the centre point of the rotated icon
                            rotated_arrow_centre_point = (rotated_arrow.width // 2, rotated_arrow.height // 2)

                            # Calculate the top-left corner of the icon based on the center point and x, y
                            top_left = (int(x) - rotated_arrow_centre_point[0], int(y) - rotated_arrow_centre_point[1])

                            for plan in plans:
                                plan.paste(rotated_arrow, top_left, mask=rotated_arrow)

                            deviation = 30

                            if (180 - deviation) < angle < (180 + deviation):
                                # Override y_offsetter the text below the AP icon
                                y_offsetter = arrow.height / 1.9

                        else:
                            # Calculate the top-left corner of the icon based on the center point and x, y
                            top_left = (int(x) - arrow_centre_point[0], int(y) - arrow_centre_point[1])

                            for plan in plans:
                                # Paste the arrow onto the floorplan at the calculated location
                                plan.paste(spot, top_left, mask=spot)

                        #  Define ap_info text
                        ap_info = (
                            f"AP Name: {ap['name']}{nl}"
                            f"AP Vendor: {ap['vendor']}{nl}"
                            f"AP Model: {ap['model']}{nl}"
                            f"AP Mount: {antennaMounting}{nl}"
                            f"AP Height: {antennaHeight}{nl}"
                            f"Antenna Tilt: {antennaTilt}")

                        if ap_note:
                            ap_info = ap_info + f"{nl}Notes: {ap_note}"

                        if ap_tags:
                            ap_info = ap_info + f"{nl}Tags: {ap_tags}"

                        # Calculate the height and width of the text
                        text_width, text_height = text_width_and_height_getter(ap_info)

                        # Calculate the crop box for the new image
                        crop_box = (x - crop_size // 2, y - crop_size // 2, x + crop_size // 2, y + crop_size // 2)

                        # Crop the image
                        cropped_image = isolated_AP.crop(crop_box)

                        draw_isolated_AP = ImageDraw.Draw(cropped_image)

                        # Establish coordinates for the ap_info rounded rectangle
                        # Keep ap_info box away from the edges of the cropped AP image
                        edge_buffer = 100

                        x1 = crop_size - edge_buffer - text_width - (offset * 2)
                        y1 = edge_buffer - (offset * 2)

                        x2 = crop_size - edge_buffer + offset
                        y2 = edge_buffer + text_height + offset

                        # Corner radius
                        r = 20

                        # draw the ap_info rounded rectangle
                        draw_isolated_AP.rounded_rectangle((x1, y1, x2, y2), r, fill='white', outline='black', width=2)

                        # draw the ap_info text
                        draw_isolated_AP.text(
                            (crop_size - 100 - (text_width / 2), 100 + text_height / 2 - 5),
                            ap_info, anchor='mm', fill='black', font=font)

                        # Save the cropped image with a new filename
                        cropped_image.save(Path(zoomed_AP_destination / (ap['name'] + '-zoomed')).with_suffix('.png'))

                        # Handle AP Names drawn onto overview maps
                        ap_name = ap['name']

                        # Calculate the height and width of the text
                        text_width, text_height = text_width_and_height_getter(ap_name)

                        # Establish coordinates for the rounded rectangle
                        x1 = x - (text_width / 2) - offset
                        y1 = y + y_offsetter - (text_height / 2) - offset
                        x2 = x + (text_width / 2) + offset
                        y2 = y + y_offsetter + (text_height / 2) + offset
                        r = (y2 - y1) / 3

                        # draw the rounded rectangle
                        draw_all_APs.rounded_rectangle((x1, y1, x2, y2), r, fill='white', outline='black', width=2)

                        # draw the text
                        draw_all_APs.text((x, y + y_offsetter + 2), ap_name, anchor='mm', fill='black', font=font)

                # Remove raw floorplan source files
                os.remove(floor['imageId'])

                # Save the modified image
                all_APs.save(Path(annotated_floorplan_destination / floor['name']).with_suffix('.png'))

            try:
                shutil.rmtree(project_name)
                print(f'Temporary project contents directory removed{nl}')
            except Exception as e:
                print(e)


if __name__ == "__main__":
    start_time = time.time()
    main()
    run_time = time.time() - start_time
    print(f'** Time to run: {round(run_time, 2)} seconds **')
