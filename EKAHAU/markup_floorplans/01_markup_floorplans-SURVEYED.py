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

nl = "\n"

# SUPER DUPER user-friendly variables for tweaking output
#########################################################
# AP icon
# output size, this will depend on the resolution of the floor plans
icon_resize = 200

# TEXT
font_size = 20

# distance between AP icon centre point and top of text
# this is probably somewhere around icon_resize / 4
y_offsetter = 55

# ROUNDED RECTANGLE
# how much space between text and the edge of the rounded rectangle do you want
offset = 5

# add additional space before text
text_pad_pre = 0

# add additional space after text
text_pad_post = 0

rounded_rect_border_width = 2

colourise_rounded_rect_border = False

colourise_rounded_rect_fill = False


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
        if (file.suffix == ".esx") and (not ("re-zip" in file.stem)):
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

            # Load the "surveyed" accessPoints.json file into the surveyedAPs dictionary
            with open(Path(project_name) / "accessPoints.json") as json_file:
                surveyedAPs = json.load(json_file)
            # pprint(simulatedRadios)

            # Create an intermediary dictionary to lookup surveyed radio parameters
            surveyedAPsDict = {}

            # Populate the intermediary dictionary
            for surveyedAP in surveyedAPs["accessPoints"]:
                if "color" in surveyedAP:
                    surveyedAPsDict[surveyedAP["id"]] = {}  # initialize nested dictionary
                    surveyedAPsDict[surveyedAP["id"]]["name"] = surveyedAP["name"]
                    surveyedAPsDict[surveyedAP["id"]]["color"] = surveyedAP["color"]
                    surveyedAPsDict[surveyedAP["id"]]["floorPlanId"] = surveyedAP["location"]["floorPlanId"]
                    surveyedAPsDict[surveyedAP["id"]]["userDefinedPosition"] = surveyedAP["userDefinedPosition"]
                    for x, y in surveyedAP["location"]["coord"].items():
                        surveyedAPsDict[surveyedAP["id"]][x] = y

            # Create directory to hold output directories
            create_directory(Path.cwd() / "OUTPUT")

            # Create subdirectory for Annotated floorplans
            annotated_floorplan_destination = Path.cwd() / "OUTPUT" / "annotated"
            create_directory(annotated_floorplan_destination)

            # Import custom icons
            spot = Image.open(Path.cwd().parent / "assets" / "custom" / "spot.png")

            # Resize icons if necessary (default size is 350x350 px)
            icon_resize = 200

            spot = spot.resize((icon_resize, icon_resize))

            # Define the centre point of the icon
            spot_centre_point = (icon_resize // 2, icon_resize // 2)

            for floor in floorPlans["floorPlans"]:
                # Extract floorplans
                shutil.copy((Path(project_name) / ("image-" + floor["imageId"])), floor["imageId"])

                # Open the floorplan to be used for all AP placement
                all_APs = Image.open(floor["imageId"])

                # Create an ImageDraw object
                draw_all_APs = ImageDraw.Draw(all_APs)

                for ap in surveyedAPsDict:

                    if surveyedAPsDict.get(ap).get("floorPlanId") == floor["id"]:
                        # establish x and y
                        x, y = (surveyedAPsDict.get(ap).get("x"), surveyedAPsDict.get(ap).get("y"))

                        print(
                            f'{nl}[[ {surveyedAPsDict.get(ap).get("name")} ]] from: {floorPlanGetter(surveyedAPsDict.get(ap).get("floorPlanId"))} ]'
                            f"has coordinates {x}, {y}")

                        # Calculate the top-left corner of the icon based on the center point and x, y
                        top_left = (int(x) - spot_centre_point[0], int(y) - spot_centre_point[1])

                        # Paste the spot onto the floorplan at the calculated location
                        all_APs.paste(spot, top_left, mask=spot)

                        # Handle AP Names drawn onto overview maps
                        ap_name = surveyedAPsDict.get(ap).get("name")

                        # Calculate the height and width of the text
                        text_width, text_height = text_width_and_height_getter(ap_name)

                        # Establish coordinates for the rounded rectangle
                        x1 = x - (text_width / 2) - offset - text_pad_pre
                        y1 = y + y_offsetter - (text_height / 2) - offset
                        x2 = x + (text_width / 2) + offset + text_pad_post
                        y2 = y + y_offsetter + (text_height / 2) + offset
                        r = (y2 - y1) / 3

                        # define colour of rounded rectangle border
                        if not colourise_rounded_rect_border:
                            rounded_rect_border_color = "black"
                        else:
                            rounded_rect_border_color = surveyedAPsDict.get(ap).get("color")

                        # define colour of rounded rectangle fill
                        if not colourise_rounded_rect_fill:
                            rounded_rect_fill_color = "white"
                        else:
                            rounded_rect_fill_color = surveyedAPsDict.get(ap).get("color")

                        # draw the rounded rectangle
                        draw_all_APs.rounded_rectangle((x1, y1, x2, y2), r, fill=rounded_rect_fill_color,
                                                       outline=rounded_rect_border_color, width=rounded_rect_border_width)

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
