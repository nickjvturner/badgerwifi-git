#!/usr/bin/env python3

"""
Created with [SIMULATED AP project] as the target

description
---
script unpacks Ekahau project file

extracts the floor plan image
imports a custom X marks the spot AP icon
drops an X on each AP x,y coordinate

draws a rounded rectangle containing the AP Name below each X mark


I have started using this script to create floor plan images in preparation for post-deployment surveys
These unobtrusive AP location markers make it easy:
    know the intended AP Name
    know the intended AP location
    validate a physical installation



Nick Turner
nickjvturner.com

@nickjvturner@mastodon.social

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


nl = "\n"

# SUPER DUPER user friendly variables for tweaking output

# AP icon
# output size, this will depend on the resolution of the floor plans
icon_resize = 200

# TEXT
font_size = 20

# distance between AP icon centre point and top of text
# this is probably somewhere around icon_resize / 4
y_offsetter = 50

# ROUNDED RECTANGLE
# how much space between text and the edge of the rounded rectangle do you want
offset = 5

# add additional space before text
text_pad_pre = 0

# add additional space after text
text_pad_post = 0

rounded_rect_border_width = 2


def create_directory(new_dir):
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
        return f"Directory {new_dir} Created"
    else:
        return f"Directory {new_dir} already exists"


# Define text, font and size
if platform.system() == "Windows":
    font_path = os.path.join(os.environ["SystemRoot"], "Fonts", "Consola.ttf")
    font = ImageFont.truetype(font_path, font_size)
else:
    font = ImageFont.truetype("Menlo.ttc", font_size)


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


def main():
    # Get filename and current working directory
    print(f"{nl}{Path(__file__).name}")
    print(f"working_directory: {Path.cwd()}{nl}")

    # Get local file with extension .esx
    for file in sorted(Path.cwd().iterdir()):
        # ignore files in directory containing _re-zip
        if (file.suffix == ".esx") and (not("re-zip" in file.stem)):
            proceed = input(f"Proceed with file: {str(file.name)}? (YES/no)")
            if proceed == "no":
                continue

            print("filename:", file.name)

            # Define the project name
            project_name = file.stem
            print("project_name:", project_name)

            # Unzip the .esx project file into folder named {project_name}
            with zipfile.ZipFile(file.name, "r") as zip_ref:
                zip_ref.extractall(project_name)
            print("project successfully unzipped")

            # Load the floorPlans.json file into the floorPlansJSON Dictionary
            with open(Path(project_name) / "floorPlans.json") as json_file:
                floorPlans = json.load(json_file)
            # pprint(floorPlans)

            # Create an intermediary dictionary to lookup floor names
            floorPlansDict = {}

            # Populate the intermediary dictionary with {floorId: floor name}
            for floor in floorPlans["floorPlans"]:
                floorPlansDict[floor["id"]] = floor["name"]
            # pprint(floorPlansDict)

            def floorPlanGetter(floorPlanId):
                # print(floorPlansDict.get(floorPlanId))
                return floorPlansDict.get(floorPlanId)

            # Load the simulatedRadios.json file into the simulatedRadios dictionary
            with open(Path(project_name) / "simulatedRadios.json") as json_file:
                simulatedRadios = json.load(json_file)
            # pprint(simulatedRadios)

            # Create an intermediary dictionary to lookup simulated radio parameters
            simulatedRadioDict = {}

            # Populate the intermediary dictionary
            for radio in simulatedRadios["simulatedRadios"]:
                simulatedRadioDict[radio["accessPointId"]] = {}  # initialize nested dictionary
                for x, y in radio.items():
                    # print(x, y)
                    simulatedRadioDict[radio["accessPointId"]][x] = y

            # pprint(simulatedRadioDict)
            # print(simulatedRadioDict["84d58cfc-1121-4b8c-97e7-c589f56494e4"]["antennaHeight"])

            # Load the accessPoints.json file into the accessPoints dictionary
            with open(Path(project_name) / "accessPoints.json") as json_file:
                accessPoints = json.load(json_file)
            # pprint(accessPoints)

            # Create directory to hold output directories
            create_directory(Path.cwd() / "OUTPUT")

            # Create subdirectory for Blank floor plans
            plain_floorplan_destination = Path.cwd() / "OUTPUT" / "blank"
            create_directory(plain_floorplan_destination)

            # Create subdirectory for Annotated floorplans
            annotated_floorplan_destination = Path.cwd() / "OUTPUT" / "annotated"
            create_directory(annotated_floorplan_destination)

            # Import custom icons
            spot = Image.open(Path.cwd().parent / "assets" / "XO.png")

            # Resize icons if necessary (default size is 350x350 px)
            icon_resize = 200

            spot = spot.resize((icon_resize, icon_resize))

            # Define the centre point of the icon
            spot_centre_point = (icon_resize // 2, icon_resize // 2)

            for floor in floorPlans["floorPlans"]:
                # Extract floorplans
                shutil.copy((Path(project_name) / ("image-" + floor["imageId"])), Path(plain_floorplan_destination / floor["name"]).with_suffix(".png"))
                shutil.copy((Path(project_name) / ("image-" + floor["imageId"])), floor["imageId"])

                # Open the floorplan to be used for all AP placement
                all_APs = Image.open(floor["imageId"])

                # Create an ImageDraw object
                draw_all_APs = ImageDraw.Draw(all_APs)

                for ap in sorted(accessPoints["accessPoints"], key=lambda i: i["name"]):
                    # print(ap)
                    # print(ap["location"]["floorPlanId"])

                    if ap["location"]["floorPlanId"] == floor["id"]:

                        # establish x and y
                        x, y = (ap["location"]["coord"]["x"], ap["location"]["coord"]["y"])

                        print(
                            f'{nl}[[ {ap["name"]} [{ap["model"]}]] from: {floorPlanGetter(ap["location"]["floorPlanId"])} ] '
                            f"has coordinates {x}, {y}")

                        # Calculate the top-left corner of the icon based on the center point and x, y
                        top_left = (int(x) - spot_centre_point[0], int(y) - spot_centre_point[1])

                        # Paste the spot onto the floorplan at the calculated location
                        all_APs.paste(spot, top_left, mask=spot)

                        # Handle AP Names drawn onto overview maps
                        ap_name = ap["name"]

                        # Calculate the height and width of the text
                        text_width, text_height = text_width_and_height_getter(ap_name)

                        # Establish coordinates for the rounded rectangle
                        x1 = x - (text_width / 2) - offset - text_pad_pre
                        y1 = y + y_offsetter - (text_height / 2) - offset
                        x2 = x + (text_width / 2) + offset + text_pad_post
                        y2 = y + y_offsetter + (text_height / 2) + offset
                        r = (y2 - y1) / 3

                        # draw the rounded rectangle
                        draw_all_APs.rounded_rectangle((x1, y1, x2, y2), r, fill="white", outline="black", width=rounded_rect_border_width)

                        # draw the text
                        draw_all_APs.text((x + 1, y + y_offsetter + 1), ap_name, anchor="mm", fill="black", font=font)

                # Remove raw floorplan source files
                os.remove(floor["imageId"])

                # Save the modified image
                all_APs.save(Path(annotated_floorplan_destination / floor["name"]).with_suffix(".png"))

            try:
                shutil.rmtree(project_name)
                print(f"Temporary project contents directory removed{nl}")
            except Exception as e:
                print(e)


if __name__ == "__main__":
    start_time = time.time()
    main()
    run_time = time.time() - start_time
    print(f"** Time to run: {round(run_time, 2)} seconds **")
