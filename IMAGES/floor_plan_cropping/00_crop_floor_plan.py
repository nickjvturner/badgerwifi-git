#!/usr/bin/env python3
"""
Written by Nick Turner (@nickjvturner@mastodon.social)

When you 'export' an image from Ekahau using Reporting > Export Image
Ekahau adds an 80 pixel bar to the bottom of the image, if you are exporting
a visualisation this bar houses the legend, if you are simply exporting
an AP location map, this bar is just an empty white bar, added to the foot of
the floor plan.

This is a problem if you 'ever' wanted to re-import the map into Ekahau.

This script will iterate through the script root directory
any .png or .jpg files will be modified
remove 80 pixels from the bottom edge
convert to greyscale
boost the contrast

save the output image into an output folder
"""

from pathlib import Path
import time
import os

try:
	from PIL import Image, ImageDraw, ImageFont, ImageEnhance
except ImportError as e:
	print(e.msg)
	print('You need to install Python Image Library (Pillow)')
	print('pip install Pillow')

def create_directory(directory_name):
	if not os.path.exists(directory_name):
		os.mkdir(directory_name)
		print(f'Directory {directory_name} Created {nl}')
	else:
		print(f'Directory {directory_name} already exists {nl}')

nl = '\n'

def main():
	outputdir = Path.cwd() / 'cropped image output'

	# Create a new directory to place the new Images
	create_directory(outputdir)

	for file in Path.cwd().iterdir():
		if file.suffix == '.png' or file.suffix == '.jpg':
			im = Image.open(file)

			try:
				# Get the image size
				width, height = im.size

				# Define the new height after removing 80 pixels from the bottom
				new_height = height - 80

				# Crop the image to the new dimensions (left, upper, right, lower)
				# cropped_image = im.crop((1, 0, (width - 1), new_height))
				cropped_image = im.crop((0, 0, width, new_height))

				# Convert the cropped image to black and white
				bw_image = cropped_image.convert("L")

				# Adjust the brightness (0.5 means 50% brightness)
				enhancer = ImageEnhance.Brightness(bw_image)
				brightened_image = enhancer.enhance(1.5)

				# Save the resulting image
				brightened_image.save(outputdir / Path(file.name))

			except Exception as e:
				print(e.msg)

			finally:
				# Close the image files
				im.close()
				bw_image.close()
				brightened_image.close()


if __name__ == "__main__":
	start_time = time.time()
	main()
	run_time = time.time() - start_time
	print(f'** Time to run: {round(run_time, 2)} seconds **')
