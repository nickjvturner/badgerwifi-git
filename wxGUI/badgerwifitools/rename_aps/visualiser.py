import wx
import platform

import matplotlib.image as mpimg
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from pathlib import Path
import importlib.util

from common import load_json
from common import create_floor_plans_dict
from common import model_antenna_split

from common import discover_available_scripts
from common import RENAME_APS_DIR
from common import BOUNDARY_SEPARATION_WIDGET

from rename_aps.ap_renamer import ap_renamer


def import_module_from_path(module_name, path_to_module):
    spec = importlib.util.spec_from_file_location(module_name, path_to_module)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MapDialog(wx.Dialog):
    """A dialog for displaying maps and access point information."""
    def __init__(self, parent, title, ap_data, map_data, floor_plans_dict, initial_dropdown_selection):
        super().__init__(parent, title=title, size=(1000, 800))
        self.set_window_size()
        self.ap_data = ap_data
        self.map_data = map_data
        self.current_map = next(iter(map_data))
        self.floor_plans_dict = floor_plans_dict
        self.current_dropdown_selection = initial_dropdown_selection

        self.current_sorting_module = None
        self.image_cache = {}  # Cache for loaded images
        self.boundary_separation = parent.rename_aps_boundary_separator
        self.update_boundary_separator_value = parent.update_boundary_separator_value
        self.boundaries = None

        self.parent = parent

        self.init_ui()

    def set_window_size(self):
        if platform.system() == 'Windows':
            # Set the frame size to the minimum size
            self.SetSize((1000, 700))
            self.edge_margin = 0
        if platform.system() == 'Darwin':
            # Set the frame size to the minimum size
            self.edge_margin = 5

    def init_ui(self):
        """Initialize the user interface."""
        self.panel = wx.Panel(self)
        self.setup_buttons()
        self.setup_labels()
        self.setup_dropdowns()
        self.setup_figure()
        self.setup_layout()
        self.on_rename_change(None)

    def setup_buttons(self):
        self.dismiss_button = wx.Button(self.panel, label='Dismiss')
        self.dismiss_button.Bind(wx.EVT_BUTTON, self.on_dismiss)

        self.rename_aps_button = wx.Button(self.panel, label='Rename APs')
        self.rename_aps_button.Bind(wx.EVT_BUTTON, self.on_rename_aps)

    def setup_labels(self):
        """Setup the labels for the dialog."""
        self.rename_script_one_liner = wx.StaticText(self.panel, label="")

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
        self.row1.Add(self.rename_choice, 0, wx.EXPAND | wx.ALL, self.edge_margin)
        self.row1.AddStretchSpacer()

        self.action_row = wx.BoxSizer(wx.HORIZONTAL)
        self.action_row.Add(self.rename_script_one_liner, 0, wx.EXPAND | wx.ALL, 5)
        self.action_row.AddStretchSpacer()
        self.action_row.Add(self.rename_aps_button, 0, wx.EXPAND | wx.ALL, self.edge_margin)

        self.exit_row = wx.BoxSizer(wx.HORIZONTAL)
        self.exit_row.AddStretchSpacer()
        self.exit_row.Add(self.dismiss_button, 0, wx.EXPAND | wx.ALL, self.edge_margin)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.row1, 0, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.action_row, 0, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.exit_row, 0, wx.EXPAND | wx.ALL, 5)

        self.panel.SetSizer(self.main_sizer)
        self.Centre()

    def on_map_change(self, event):
        """Handle map selection changes."""
        self.current_map = self.map_choice.GetStringSelection()
        self.update_plot()

    def on_rename_change(self, event):
        """Handle rename script selection changes."""
        self.boundaries = None
        selected_script = self.rename_choice.GetStringSelection()
        path_to_module = Path(__file__).resolve().parent.parent / RENAME_APS_DIR / f'{selected_script}.py'
        self.current_sorting_module = import_module_from_path(selected_script, path_to_module)

        # Update the one-liner label with a description from the selected module
        if hasattr(self.current_sorting_module, 'ONE_LINER_DESCRIPTION'):
            self.rename_script_one_liner.SetLabel(self.current_sorting_module.ONE_LINER_DESCRIPTION)

        # Remove existing boundary_separation widgets if they exist
        if hasattr(self, 'spin_ctrl'):
            self.remove_boundary_separation_widget()

        # Add the boundary separator widgets only if the selected script has attribute "visualise_boundaries"
        if hasattr(self.current_sorting_module, BOUNDARY_SEPARATION_WIDGET):
            self.add_boundary_separation_widget()

        self.panel.Layout()  # Re-layout the panel to reflect changes
        self.update_plot()  # Update plot or other UI elements as necessary

    def add_boundary_separation_widget(self):
        """Add boundary separation widget based on the current sorting module."""
        # Logic from on_rename_change for adding widgets
        self.spin_ctrl_label = wx.StaticText(self.panel, label="Boundary Separator:")

        self.spin_ctrl = wx.SpinCtrl(self.panel, value='0')
        self.spin_ctrl.SetRange(0, 10000)  # Set minimum and maximum values
        self.spin_ctrl.SetValue(400)  # Set the initial value
        self.spin_ctrl.SetIncrement(10)  # Set the increment value (step size)

        self.update_button = wx.Button(self.panel, label='Update')
        self.update_button.Bind(wx.EVT_BUTTON, self.on_spin)

        self.row1.Add(self.spin_ctrl_label, 0, wx.ALL, 5)
        self.row1.Add(self.spin_ctrl, 0, wx.ALIGN_CENTER_VERTICAL, 1)
        self.row1.Add(self.update_button, 0, wx.ALL, 5)

    def remove_boundary_separation_widget(self):
        """Remove any existing boundary_separation widgets."""
        # Logic from on_rename_change for removing widgets
        self.row1.Detach(self.spin_ctrl)  # Detach from sizer
        self.spin_ctrl.Destroy()  # Destroy the widget
        del self.spin_ctrl  # Remove the attribute to avoid reusing it

        self.row1.Detach(self.spin_ctrl_label)
        self.spin_ctrl_label.Destroy()  # Destroy the widget
        del self.spin_ctrl_label  # Remove the attribute to avoid reusing it

        self.row1.Detach(self.update_button)
        self.update_button.Destroy()
        del self.update_button

    def on_spin(self, event):
        self.boundary_separation = int(self.spin_ctrl.GetValue())
        self.update_boundary_separator_value(self.boundary_separation)
        self.update_plot()

    def on_show(self, event):
        self.map_choice.SetSelection(0)
        self.rename_choice.SetSelection(0)
        self.update_plot()

    def update_plot(self):
        """High-level plot update management."""
        with wx.BusyCursor():
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            self.load_image_and_plot(ax)
            self.plot_aps(ax)
            self.draw_connections(ax)
            self.plot_boundaries(ax)
            self.figure.tight_layout()
            self.canvas.draw()

    def load_image_and_plot(self, ax):
        """Load and plot the current map image."""
        img_path = self.map_data[self.current_map][0]
        img = self.load_image(img_path)  # Use cached image
        ax.imshow(img)
        ax.axis('off')

    def plot_aps(self, ax):
        """Plot APs on the map."""
        self.sorted_aps_list, self.boundaries, self.boundary_orientation = self.get_sorted_aps_list()
        for i, ap in enumerate(self.sorted_aps_list, start=1):
            ax.scatter(ap['location']['coord']['x'], ap['location']['coord']['y'], color=ap['color'], s=250, zorder=5)
            ax.text(ap['location']['coord']['x'], ap['location']['coord']['y'], str(i), color='black', ha='center', va='center', zorder=6)

    def draw_connections(self, ax):
        """Draw connections between APs and any additional markers, with each segment in a different color."""
        # Ensure there are at least two points to connect.
        if len(self.sorted_aps_list) > 1:
            for i in range(len(self.sorted_aps_list) - 1):
                # Extract start and end points for the segment.
                start_point = (self.sorted_aps_list[i]['location']['coord']['x'], self.sorted_aps_list[i]['location']['coord']['y'])
                end_point = (self.sorted_aps_list[i + 1]['location']['coord']['x'], self.sorted_aps_list[i + 1]['location']['coord']['y'])

                if hasattr(self.current_sorting_module, 'connections_colour_logic'):
                    segment_color, linestyle, linewidth = self.current_sorting_module.connections_colour_logic()

                else:
                    # Determine the color for this segment.
                    segment_color = self.sorted_aps_list[i]['color']  # Or some logic to choose the color.

                    # Initialize default linestyle
                    linestyle = '-'
                    linewidth = 3

                    if hasattr(self.current_sorting_module, 'SPLIT_BOUNDARY_GROUPS'):
                        # Change linestyle for differently colored APs
                        if self.sorted_aps_list[i]['color'] != self.sorted_aps_list[i + 1]['color']:
                            linestyle = ':'  # Dashed line for differently colored APs
                            segment_color = 'grey'  # Change the color to grey for dashed lines
                            linewidth = 1

                        # Check for different x or y group and change linestyle accordingly
                        different_group = False
                        if self.boundary_orientation == 'horizontal':
                            if self.sorted_aps_list[i]['location']['coord']['y_group'] != self.sorted_aps_list[i + 1]['location']['coord']['y_group']:
                                different_group = True
                        if self.boundary_orientation == 'vertical':
                            if self.sorted_aps_list[i]['location']['coord']['x_group'] != self.sorted_aps_list[i + 1]['location']['coord']['x_group']:
                                different_group = True

                        if different_group and segment_color != 'grey':
                            linestyle = '--'  # Dotted line for different grouped APs
                            linewidth = 2

                # Draw the line segment with the specified color and linestyle
                ax.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], color=segment_color, linestyle=linestyle, linewidth=linewidth, zorder=4)

    def get_sorted_aps_list(self):
        """Obtain the sorted list of APs and any additional data, such as boundaries."""
        ap_list = []
        for ap in self.ap_data.values():
            if ap['floor'] == self.current_map:
                ap_list.append(ap)

        if self.current_sorting_module and hasattr(self.current_sorting_module, BOUNDARY_SEPARATION_WIDGET):
            return self.current_sorting_module.sort_logic(ap_list, self.floor_plans_dict, self.boundary_separation, True)

        elif self.current_sorting_module and hasattr(self.current_sorting_module, "sort_logic"):
            return self.current_sorting_module.sort_logic(ap_list, self.floor_plans_dict), None, None  # Adjust as per the sorting function's requirements

    def plot_boundaries(self, ax):
        if self.boundaries is None:
            return

        elif self.boundary_orientation == 'horizontal':
            self.draw_row_indicators(ax)
            for boundary in self.boundaries:
                ax.axhline(y=boundary, color='b', linestyle='--', linewidth=1)
            # Skip drawing the last boundary if it's beyond the plot's limits
            if self.boundaries[-1] + self.boundary_separation < ax.get_ylim()[1]:
                ax.axhline(y=boundary + self.boundary_separation, color='b', linestyle='--', linewidth=1)  # Draw the last boundary

        elif self.boundary_orientation == 'vertical':
            self.draw_column_indicators(ax)
            for boundary in self.boundaries:
                ax.axvline(x=boundary, color='b', linestyle='--', linewidth=1)
            ax.axvline(x=boundary + self.boundary_separation, color='b', linestyle='--', linewidth=1)  # Draw the last boundary

    def draw_row_indicators(self, ax):
        """Draw indicators for row numbers between boundary lines."""
        plot_xlim = ax.get_xlim()
        x_position = plot_xlim[0]  # You might want to adjust this to not overlap with your plot

        for i, y_position in enumerate(self.boundaries, start=1):
            # Place the row indicator. Adjust `x_position` and `y_position` as needed.
            # You might want to add or subtract a small value to `y_position` to avoid overlap with the lines
            ax.text(x_position, y_position + (self.boundary_separation / 2), f"{i}", verticalalignment='center', horizontalalignment='left', color='blue', fontsize=10)

    def draw_column_indicators(self, ax):
        """Draw indicators for column numbers between boundary lines."""
        plot_ylim = ax.get_ylim()
        y_position = plot_ylim[0]  # Adjust as needed, depending on where you want the text

        for i, x_position in enumerate(self.boundaries, start=1):
            # Similar to rows, but now we're adjusting the x positions for column indicators
            ax.text(x_position + (self.boundary_separation / 2), y_position, f"{i}", verticalalignment='bottom', horizontalalignment='center', color='blue', fontsize=10)

    def on_dismiss(self, event):
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()

    def on_rename_aps(self, event):
        ap_renamer(self.parent.working_directory, self.parent.esx_project_name, self.current_sorting_module, self.parent.append_message, self.boundary_separation)


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

    for key, value in sorted(floor_plans_dict_reversed.items()):
        floor_file_id = 'image-' + key
        map_data.setdefault(value, []).append(working_directory / project_name / floor_file_id)

    # Launch the MapDialog as modal
    dialog = MapDialog(parent_frame, "AP Visualization", ap_data, map_data, floor_plans_dict, current_dropdown_selection)
    dialog.ShowModal()  # Display the dialog modally
    dialog.Destroy()  # Ensure to destroy the dialog after it's closed
