import wx

import matplotlib.image as mpimg
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure

from common import load_json
from common import create_floor_plans_dict
from common import model_antenna_split
from pathlib import Path

from common import discover_available_scripts
from common import RENAME_APS_DIR

import importlib.util


def import_module_from_path(module_name, path_to_module):
    spec = importlib.util.spec_from_file_location(module_name, path_to_module)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MapDialog(wx.Dialog):
    """A dialog for displaying maps and access point information."""
    def __init__(self, parent, title, ap_data, map_data, floor_plans_dict, initial_dropdown_selection):
        super().__init__(parent, title=title, size=(1000, 900))
        self.ap_data = ap_data
        self.map_data = map_data
        self.current_map = next(iter(map_data))
        self.current_sorting_module = None
        self.floor_plans_dict = floor_plans_dict
        self.current_dropdown_selection = initial_dropdown_selection

        self.image_cache = {}  # Cache for loaded images
        self.y_axis_threshold = 400

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.panel = wx.Panel(self)
        self.setup_buttons()
        self.setup_dropdowns()
        self.setup_figure()
        self.setup_layout()
        self.on_rename_change(None)

    def setup_buttons(self):
        self.dismiss_button = wx.Button(self.panel, label='Dismiss')
        self.dismiss_button.Bind(wx.EVT_BUTTON, self.on_dismiss)

    def setup_dropdowns(self):
        """Setup the dropdown menus."""
        self.map_choice = wx.Choice(self.panel, choices=sorted(self.map_data.keys()))
        self.map_choice.Bind(wx.EVT_CHOICE, self.on_map_change)

        self.rename_choice = wx.Choice(self.panel, choices=discover_available_scripts(RENAME_APS_DIR))
        self.rename_choice.Bind(wx.EVT_CHOICE, self.on_rename_change)
        self.rename_choice.SetSelection(self.current_dropdown_selection)

    def setup_figure(self):
        """Setup the matplotlib figure."""
        self.figure = Figure()
        self.canvas = FigureCanvas(self.panel, -1, self.figure)

    def load_image(self, img_path):
        """Load and cache the image to avoid redundant disk reads."""
        if img_path not in self.image_cache:
            self.image_cache[img_path] = mpimg.imread(img_path)
        return self.image_cache[img_path]

    def setup_layout(self):
        """Setup the layout of the dialog."""
        self.row1 = wx.BoxSizer(wx.HORIZONTAL)
        self.row1.Add(self.map_choice, 0, wx.EXPAND | wx.ALL, 5)
        self.row1.Add(self.rename_choice, 0, wx.EXPAND | wx.ALL, 5)
        self.row1.AddStretchSpacer()

        self.exit_row = wx.BoxSizer(wx.HORIZONTAL)
        self.exit_row.AddStretchSpacer()
        self.exit_row.Add(self.dismiss_button, 0, wx.EXPAND | wx.ALL, 5)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.row1, 0, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.exit_row, 0, wx.EXPAND | wx.ALL, 5)

        self.panel.SetSizer(self.main_sizer)
        self.Centre()

    def on_map_change(self, event):
        """Handle map selection changes."""
        self.current_map = self.map_choice.GetStringSelection()
        self.update_plot()

    def on_rename_change(self, event):
        """Handle rename script selection changes."""
        selected_script = self.rename_choice.GetStringSelection()
        path_to_module = Path(__file__).resolve().parent / f'{selected_script}.py'
        self.current_sorting_module = import_module_from_path(selected_script, path_to_module)

        # Remove existing dynamic widget if it exists
        if hasattr(self, 'spin_ctrl'):
            self.remove_dynamic_widgets()

        # Add a new widget only if the selected script has attribute "dynamic_widget"
        # Inside the on_rename_change method, modify the creation of the dynamic_widget
        if hasattr(self.current_sorting_module, 'dynamic_widget'):
            self.add_dynamic_widgets()

        self.panel.Layout()  # Re-layout the panel to reflect changes
        self.update_plot()  # Update plot or other UI elements as necessary

    def add_dynamic_widgets(self):
        """Add dynamic widgets based on the current sorting module."""
        # Logic from on_rename_change for adding widgets
        self.spin_ctrl_label = wx.StaticText(self.panel, label="y axis threshold:")

        self.spin_ctrl = wx.SpinCtrl(self.panel, value='0')
        self.spin_ctrl.SetRange(0, 10000)  # Set minimum and maximum values
        self.spin_ctrl.SetValue(400)  # Set the initial value
        self.spin_ctrl.SetIncrement(50)  # Set the increment value (step size)
        self.spin_ctrl.Bind(wx.EVT_SPINCTRL, self.on_spin)  # Bind to its event

        self.row1.Add(self.spin_ctrl_label, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        self.row1.Add(self.spin_ctrl, 0, wx.ALIGN_CENTER_VERTICAL, 1)

    def remove_dynamic_widgets(self):
        """Remove any existing dynamic widgets."""
        # Logic from on_rename_change for removing widgets
        self.row1.Detach(self.spin_ctrl)  # Detach from sizer
        self.spin_ctrl.Destroy()  # Destroy the widget
        del self.spin_ctrl  # Remove the attribute to avoid reusing it

        self.row1.Detach(self.spin_ctrl_label)  # Detach from sizer
        self.spin_ctrl_label.Destroy()  # Destroy the widget
        del self.spin_ctrl_label  # Remove the attribute to avoid reusing it

    def on_y_axis_threshold_change(self, event):
        self.y_axis_threshold = int(self.spin_ctrl.GetValue())
        self.update_plot()

    def on_spin(self, event):
        self.y_axis_threshold = int(self.spin_ctrl.GetValue())
        self.update_plot()

    def on_show(self, event):
        self.map_choice.SetSelection(0)
        self.rename_choice.SetSelection(0)
        self.update_plot()

    def update_plot(self):
        """Update the plot with the current map and AP data."""
        boundaries = None
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        img_path = self.map_data[self.current_map][0]
        img = self.load_image(img_path)  # Use cached image
        ax.imshow(img)

        ap_list = []
        for ap in self.ap_data.values():
            if ap['floor'] == self.current_map:
                ap_list.append(ap)

        if self.current_sorting_module and hasattr(self.current_sorting_module, "visualise_centre_rows"):
            sorted_aps_list, boundaries = self.current_sorting_module.sort_logic(ap_list, self.floor_plans_dict, self.y_axis_threshold, True)

        elif self.current_sorting_module and hasattr(self.current_sorting_module, "sort_logic"):
            sorted_aps_list = self.current_sorting_module.sort_logic(ap_list, self.floor_plans_dict)  # Adjust as per the sorting function's requirements

        # Prepare lists of x and y coordinates
        x_coords = [ap['location']['coord']['x'] for ap in sorted_aps_list]
        y_coords = [ap['location']['coord']['y'] for ap in sorted_aps_list]

        # Plot APs with new IDs based on their sorted position
        for i, ap in enumerate(sorted_aps_list, start=1):
            ax.scatter(ap['location']['coord']['x'], ap['location']['coord']['y'], color=ap['color'], s=250, zorder=5)
            ax.text(ap['location']['coord']['x'], ap['location']['coord']['y'], str(i), color='black', ha='center', va='center', zorder=6)

        # Draw lines connecting the points
        # Check if there are at least two points to connect
        if len(x_coords) > 1:
            ax.plot(x_coords, y_coords, color='gray', linestyle='-', linewidth=2, zorder=4)  # Adjust color, linestyle, and linewidth as needed

        # Calculate and draw horizontal row boundaries
        if boundaries is not None:
            for boundary in boundaries:
                ax.axhline(y=boundary, color='b', linestyle='--', linewidth=1)  # Draw the first line

        ax.axis('off')
        self.figure.tight_layout()
        self.canvas.draw()

    def on_dismiss(self, event):
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()


def create_custom_ap_dict(access_points_json, floor_plans_dict):
    custom_ap_dict = {}
    for ap in access_points_json['accessPoints']:
        ap_model, external_antenna, antenna_description = model_antenna_split(ap.get('model', ''))

        custom_ap_dict[ap['name']] = {
            'name': ap['name'],
            'color': ap.get('color', 'grey'),
            'model': ap_model,
            'floor': floor_plans_dict.get(ap['location']['floorPlanId']).get('name'),
            'location': ap['location'],
            'floorPlanName': floor_plans_dict.get(ap['location']['floorPlanId'])
            }

    return custom_ap_dict


def create_reversed_floor_plans_dict(floor_plans_json):
    """Create a dictionary of floor plans."""
    floor_plans_dict = {}
    for floor in floor_plans_json['floorPlans']:
        floor_plans_dict[floor['imageId']] = floor['name']
    return floor_plans_dict


def visualise_ap_renaming(working_directory, project_name, message_callback, current_dropdown_selection, parent_frame):
    floor_plans_json = load_json(working_directory / project_name, 'floorPlans.json', message_callback)
    access_points_json = load_json(working_directory / project_name, 'accessPoints.json', message_callback)

    floor_plans_dict_reversed = create_reversed_floor_plans_dict(floor_plans_json)
    floor_plans_dict = create_floor_plans_dict(floor_plans_json)
    ap_data = create_custom_ap_dict(access_points_json, floor_plans_dict)

    # Prepare map_data
    map_data = {}

    for key, value in floor_plans_dict_reversed.items():
        floor_file_id = 'image-' + key
        map_data.setdefault(value, []).append(working_directory / project_name / floor_file_id)

    # Launch the MapDialog as modal
    dialog = MapDialog(parent_frame, "AP Visualization", ap_data, map_data, floor_plans_dict, current_dropdown_selection)
    dialog.ShowModal()  # Display the dialog modally
    dialog.Destroy()  # Ensure to destroy the dialog after it's closed
