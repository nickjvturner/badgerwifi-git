import shutil

from common import load_json
from esx_actions.rebundle_esx import rebundle_project


def create_pds_project_esx(self, message_callback):
    # Validate directories
    pds_maps_dir = self.working_directory / 'OUTPUT' / 'PDS AP location maps'
    project_dir = self.working_directory / self.esx_project_name

    if not pds_maps_dir.exists():
        message_callback("PDS maps directory not found. Run the PDS map creator first.")
        return

    # Load and validate JSON
    floor_plans_json = load_json(project_dir, 'floorPlans.json', message_callback)
    if not floor_plans_json:
        message_callback("Error: Failed to load floorPlans.json.")
        return

    # Create a temporary directory inside the working directory
    temp_dir = self.working_directory / f"{self.esx_project_name}_temp"
    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)  # Clean up any existing temp directory
        temp_dir.mkdir()

        # Copy the project directory into the temporary directory
        temp_project_dir = temp_dir / self.esx_project_name
        shutil.copytree(project_dir, temp_project_dir)

        message_callback(f"Temporary directory created: {temp_dir}")

        # Process and replace images in the temporary directory
        for floor in sorted(floor_plans_json['floorPlans'], key=lambda i: i['name']):
            image_id = floor['imageId']
            floor_name = floor['name']
            pds_map_path = pds_maps_dir / f'{floor_name}.png'

            if not pds_map_path.exists():
                message_callback(f"Warning: Missing PDS map for {floor_name}. Skipping.")
                continue

            dest_path = temp_project_dir / f'image-{image_id}'
            shutil.copy(pds_map_path, dest_path)
            message_callback(f"Copied PDS map for {floor_name} to {dest_path}.")

        # Remove unnecessary JSON files in the temporary directory
        if hasattr(self, 'project_profile_module'):
            for file in getattr(self.project_profile_module, 'predictive_json_asset_deletion', []):
                file_path = temp_project_dir / f"{file}.json"
                if file_path.exists():
                    file_path.unlink()
                    message_callback(f"Removed: {file}")

        # Rebundle project from the temporary directory
        rebundle_project(temp_dir, self.esx_project_name, self.append_message)

        # Move the new .esx file to the working directory
        rebundled_file = temp_dir / f"{self.esx_project_name}_re-zip.esx"
        if rebundled_file.exists():
            shutil.move(rebundled_file, self.working_directory / f"{self.esx_project_name}.esx")
            message_callback(f"Rebundled file moved to {self.working_directory}")
        else:
            message_callback(f"Error: Rebundeled file {rebundled_file} not found.")

    except Exception as e:
        message_callback(f"Unexpected error: {e}")

    finally:
        # Clean up the temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            message_callback(f"Temporary directory {temp_dir} has been deleted.")
