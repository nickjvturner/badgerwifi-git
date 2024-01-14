#!/usr/bin/env python3
"""
Written by Nick Turner (@nickjvturner)

This script will iterate through a directory of image files
add a white border strip to the bottom edge
print the filename in black centred text within the margin
"""

import os
from pathlib import Path
import time
try:
	from PIL import Image, ImageDraw, ImageFont
except ImportError as error:
	print(error.msg)
	print('You need to install Python Image Library (Pillow)')
	print('pip install Pillow')


nl = '\nl'


def add_margin(pil_img, top, right, bottom, left, color):
	width, height = pil_img.size
	new_width = width + right + left
	new_height = height + top + bottom
	result = Image.new(pil_img.mode, (new_width, new_height), color)
	result.paste(pil_img, (left, top))
	return result


def add_caption(pil_img2, caption):
	width, height = pil_img2.size
	try:
		font = ImageFont.truetype('Avenir.ttc', 50)
	except:
		font = ImageFont.truetype('arial.ttf', 40)
	draw = ImageDraw.Draw(pil_img2)
	text_width = draw.textlength(caption, font=font)
	result = draw.text(((width/2), (height-15)), caption, fill='black', font=font, anchor='mb', align='center')
	return result


def create_directory(directory_name):
	if not os.path.exists(directory_name):
		os.mkdir(directory_name)
		print(f'Directory {directory_name} Created {nl}')
	else:
		print(f'Directory {directory_name} already exists {nl}')


def main():
	sourcedir = Path.cwd() / 'AP_images'
	outputdir = Path.cwd() / 'AP_images_captioned'

	# Create a new directory to place the new Images
	create_directory(outputdir)

	for file in sorted(sourcedir.iterdir()):
		if file.suffix == '.png' or '.jpg':
			try:
				im = Image.open(file)
			except error as error:
				print(error.msg)

			try:
				img_new = add_margin(im, 0, 0, 60, 0, (255, 255, 255))
				add_caption(img_new, file.name)
				img_new.save(outputdir / Path(file.name + '-captioned.jpg'), quality=95)
				print(f'{file.name} - border and filename added to image')
			except error as error:
				print(error.msg)
				print('Adding border and filename to image', file.name, 'failed')


if __name__ == "__main__":
	start_time = time.time()
	main()
	run_time = time.time() - start_time
	print(f'** Time to run: {round(run_time, 2)} seconds **')
