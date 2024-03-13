import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.patches as patches
from PIL import Image
import numpy as np

# List of map image file paths
map_images = [
    '/Users/nick/Desktop/esx_files/Odense/image-8b0c254d-fa77-4257-abc5-d16a1d00a84b',
    '/Users/nick/Desktop/esx_files/Odense/image-187d598e-dc4e-498f-8760-43139f275ac8',
    '/Users/nick/Desktop/esx_files/Odense/image-787b01de-de24-4022-b10b-6363cb4493fd'
]

# List of AP locations for each map (example coordinates, please update)
ap_locations = {
    0: [(100, 150), (200, 250)],  # AP locations for the first map
    1: [(120, 180), (220, 280)],  # AP locations for the second map
    2: [(140, 210), (240, 310)],  # AP locations for the third map
}

current_image_index = 0  # Start with the first image
current_ap_index = 0  # Start with the first AP location

# Load the first image and first AP location
image = Image.open(map_images[current_image_index])
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)
img_ax = plt.imshow(image)

# Circle and crop sizes
circle_radius = 10  # Initial circle radius
crop_size = 100  # Initial crop size (square side length)

# Add a circle patch for the AP location
current_ap_location = ap_locations[current_image_index][current_ap_index]
ap_circle_patch = patches.Circle(current_ap_location, circle_radius, edgecolor='b', facecolor='none')
ax.add_patch(ap_circle_patch)

# Function to update the circle and crop based on slider changes
def update(val):
    global circle_radius, crop_size
    circle_radius = slider_radius.val
    crop_size = slider_crop.val
    ap_circle_patch.set_radius(circle_radius)
    # Adjust crop area if necessary
    ax.set_xlim(current_ap_location[0] - crop_size//2, current_ap_location[0] + crop_size//2)
    ax.set_ylim(current_ap_location[1] + crop_size//2, current_ap_location[1] - crop_size//2)
    fig.canvas.draw_idle()

# Update the function to cycle through maps
def next_image(event):
    global current_image_index, current_ap_index, image, current_ap_location
    current_image_index = (current_image_index + 1) % len(map_images)
    current_ap_index = 0  # Reset AP index to show the first AP for the new map
    image = Image.open(map_images[current_image_index])
    current_ap_location = ap_locations[current_image_index][current_ap_index]
    img_ax.set_data(image)
    ap_circle_patch.center = current_ap_location
    fig.canvas.draw_idle()

# Button to cycle through AP locations
ax_ap_button = plt.axes([0.65, 0.025, 0.1, 0.04])
button_next_ap = Button(ax_ap_button, 'Next AP')

def next_ap_location(event):
    global current_ap_index, current_ap_location
    current_ap_index = (current_ap_index + 1) % len(ap_locations[current_image_index])
    current_ap_location = ap_locations[current_image_index][current_ap_index]
    ap_circle_patch.center = current_ap_location
    fig.canvas.draw_idle()

button_next_ap.on_clicked(next_ap_location)

# Sliders and existing code for circle and crop sizes here
# Existing button for cycling through images

plt.show()
