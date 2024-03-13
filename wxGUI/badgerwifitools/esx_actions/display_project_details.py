# display_project_details.py

from common import nl
from common import load_json
from PIL import Image


def create_custom_floor_plans_dict(floor_plans_json):
    """Create a dictionary of floor plans."""
    floor_plans_dict = {}
    for floor in floor_plans_json['floorPlans']:
        floor_plans_dict[floor['name']] = floor
    return floor_plans_dict


def map_bitmap_resolution_check(project_dir, bitmapImageId):
    """Check the resolution of the bitmap image."""
    bitmap_image = Image.open(project_dir / f"image-{bitmapImageId}")
    return bitmap_image.width, bitmap_image.height


def display_project_details(working_directory, project_name, message_callback):
    """Display the project details."""

    project_dir = working_directory / project_name

    message_callback(f"Project name: {project_name}")
    message_callback(f"Project directory: {project_dir}{nl}")

    display_floor_plans_dict(project_dir, message_callback)


def display_floor_plans_dict(project_dir, message_callback):
    """Display the floor plans dictionary."""

    custom_order = ['width', 'height']  # Update with your desired order

    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    custom_floor_plans_dict = create_custom_floor_plans_dict(floor_plans_json)

    for floor_plan_name, floor_plan_data in sorted(custom_floor_plans_dict.items()):
        message_callback(f"{nl}{floor_plan_name}:{nl}")

        for key in custom_order:
            if key in floor_plan_data:
                message_callback(f"{key}: {floor_plan_data[key]}")

        if floor_plan_data['cropMinX'] != 0.0 or floor_plan_data['cropMinY'] != 0.0 or floor_plan_data['cropMaxX'] != floor_plan_data['width'] or floor_plan_data['cropMaxY'] != floor_plan_data['height']:
            message_callback(f"{nl}** Map has been cropped within Ekahau **{nl}"
                             f"cropMinX: {floor_plan_data['cropMinX']}{nl}"
                             f"cropMinY: {floor_plan_data['cropMinY']}{nl}"
                             f"cropMaxX: {floor_plan_data['cropMaxX']}{nl}"
                             f"cropMaxY: {floor_plan_data['cropMaxY']}")

        if "bitmapImageId" in floor_plan_data:
            width, height = map_bitmap_resolution_check(project_dir, floor_plan_data["bitmapImageId"])
            message_callback(f"{nl}** Bitmap image dimensions **{nl}"
                             f"width: {width}{nl}"
                             f"height: {height}")


