import wx
import re
import shutil

from common import load_json
from common import nl, ERROR, HASH_BAR
from esx_actions.rebundle_esx import rebundle_project


def create_pds_project_esx(self, message_callback):
    # Validate directories
    pds_maps_dir = self.working_directory / 'OUTPUT' / 'PDS AP location maps'
    project_dir = self.working_directory / self.esx_project_name

    if not pds_maps_dir.exists():
        wx.CallAfter(message_callback, f"PDS maps directory not found. Run the PDS map creator first.")
        return

    # Load and validate JSON
    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    if not floor_plans_json:
        wx.CallAfter(message_callback, f"Error: Failed to load floorPlans.json")
        return

    # Create a temporary directory inside the working directory
    temp_dir_name = f"temp_dir"
    temp_dir = self.working_directory / temp_dir_name
    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)  # Clean up any existing temp directory
        temp_dir.mkdir()

        # Copy the project directory into the temporary directory
        temp_project_dir = temp_dir / self.esx_project_name
        shutil.copytree(project_dir, temp_project_dir)

        wx.CallAfter(message_callback, f"Temporary duplicate project directory created:{nl}{temp_project_dir}{nl}")

        # Process and replace images in the temporary directory
        for floor in sorted(floor_plans_json['floorPlans'], key=lambda i: i['name']):
            image_id = floor['imageId']
            floor_name = floor['name']
            pds_map_path = pds_maps_dir / f'{floor_name}.png'

            if not pds_map_path.exists():
                wx.CallAfter(message_callback, f"{nl}WARNING: Missing PDS map for {floor_name}. Skipping {nl}")
                continue

            dest_path = temp_project_dir / f'image-{image_id}'
            shutil.copy(pds_map_path, dest_path)
            wx.CallAfter(message_callback, f"Copied PDS map for {floor_name} into temp_dir")

        # Remove unnecessary JSON files in the temporary directory
        if hasattr(self, 'project_profile_module'):
            wx.CallAfter(message_callback, f"")
            for file in getattr(self.project_profile_module, 'predictive_json_asset_deletion', []):
                file_path = temp_project_dir / f"{file}.json"
                if file_path.exists():
                    file_path.unlink()
                    wx.CallAfter(message_callback, f"Removed: {file} from {temp_dir_name}")

        else:
            wx.CallAfter(message_callback, f"{nl}Selected project profile does not contain json asset removal instructions{nl}"
                                           f"PDS maps have been swapped in, project will be rebundled with predictive design elements still present.{nl}")

        wx.CallAfter(message_callback, f"")

        # Rebundle project from the temporary directory
        rebundle_project(temp_dir, self.esx_project_name, self.append_message)

        # Rename and move the rebundled file to the working directory
        try:
            rebundled_filename = f"{self.esx_project_name}_re-zip.esx"
            rebundled_file = temp_dir / rebundled_filename

            if rebundled_file.exists():
                # Check if the expected pattern is found in the filename
                if re.search(r' - predictive design v(\d+\.\d+)', self.esx_project_name):
                    # If pattern is found, apply the new naming convention
                    post_deployment_filename = re.sub(
                        r' - predictive design v(\d+\.\d+)',  # Match the version pattern
                        r' - post-deployment v0.1',  # Replace with the new pattern
                        self.esx_project_name
                    ) + '.esx'
                else:
                    # If pattern is not found, leave the rebundled filename unchanged
                    wx.CallAfter(message_callback, f"'predictive design vx.x' pattern NOT found in source filename")
                    post_deployment_filename = f"{self.esx_project_name}_re-zip.esx"

                destination_path = self.working_directory / post_deployment_filename

                # Move and rename the rebundled file
                shutil.move(rebundled_file, destination_path)
                wx.CallAfter(message_callback, f"{nl}Rebundled file renamed and moved to:{nl}{destination_path}{nl}")
            else:
                wx.CallAfter(message_callback, f"Error: Rebundled file {rebundled_file} not found")
        except Exception as e:
            wx.CallAfter(message_callback, f"Unexpected error while renaming file: {e}")

    finally:
        # Clean up the temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            wx.CallAfter(message_callback, f"Temporary directory {temp_dir} has been deleted")
