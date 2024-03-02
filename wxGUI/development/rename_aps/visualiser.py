import wx
from pathlib import Path
from PIL import Image, ImageDraw
import io

from common import load_json
from common import create_floor_plans_dict
from common import create_simulated_radios_dict


class FloorPlanVisualizer(wx.Frame):
    def __init__(self, parent, title, image_folder, message_callback, working_directory, project_name):
        super(FloorPlanVisualizer, self).__init__(parent, title=title, size=(800, 600))
        self.image_folder = Path(image_folder)
        self.image_files = [png for png in self.image_folder.iterdir() if png.suffix == '.png']
        self.current_image_index = 0
        self.zoom_scale = 1.0  # Initial zoom level

        self.working_directory = working_directory
        self.project_name = project_name
        self.message_callback = message_callback

        self.init_ui()
        self.Center()
        self.Show()

        message_callback(f'Performing action for: {project_name}')

        self.floor_plans_json = load_json(working_directory / project_name, 'floorPlans.json', message_callback)
        self.access_points_json = load_json(working_directory / project_name, 'accessPoints.json', message_callback)

        self.floor_plans_dict = create_floor_plans_dict(self.floor_plans_json)




    def init_ui(self):
        self.scroll_panel = wx.ScrolledWindow(self)
        self.scroll_panel.SetScrollbars(1, 1, 1, 1)
        self.image_control = wx.StaticBitmap(self.scroll_panel)
        self.load_image()

        # Navigation and Zoom buttons
        prev_button = wx.Button(self, label='Previous')
        next_button = wx.Button(self, label='Next')
        zoom_in_button = wx.Button(self, label='Zoom In')
        zoom_out_button = wx.Button(self, label='Zoom Out')
        dismiss_button = wx.Button(self, label='Dismiss')  # Dismiss button

        prev_button.Bind(wx.EVT_BUTTON, self.on_prev)
        next_button.Bind(wx.EVT_BUTTON, self.on_next)
        zoom_in_button.Bind(wx.EVT_BUTTON, self.on_zoom_in)
        zoom_out_button.Bind(wx.EVT_BUTTON, self.on_zoom_out)
        dismiss_button.Bind(wx.EVT_BUTTON, self.on_dismiss)  # Bind event


        # Button layout
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer(2)
        button_sizer.Add(prev_button, 0, wx.ALL, 5)
        button_sizer.Add(next_button, 0, wx.ALL, 5)
        button_sizer.Add(zoom_in_button, 0, wx.ALL, 5)
        button_sizer.Add(zoom_out_button, 0, wx.ALL, 5)
        button_sizer.AddStretchSpacer(1)
        button_sizer.Add(dismiss_button, 0, wx.ALL, 5)  # Add to layout


        # Main layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.scroll_panel, 1, wx.EXPAND)
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)

    def on_dismiss(self, event):
        # Close the window
        self.Close()

    def load_image(self):
        if not self.image_files:  # Check if the list is empty
            return  # Exit the function if there are no images to display

        filepath = self.image_files[self.current_image_index]
        pil_image = Image.open(filepath).convert("RGB")
        draw = ImageDraw.Draw(pil_image)  # Create a drawing context

        # Draw circles for each access point on the current floor
        for ap in self.access_points_json['accessPoints']:
            if ap['location']['floorPlanId'] == self.current_floor_plan_id:  # Ensure matching floor plan ID
                # Convert AP location to image coordinates here
                # This might involve scaling if the image resolution differs from the original floor plan
                x, y = self.convert_coordinates(ap['location']['coord'])
                draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill='black')  # Draw a small black circle

        # Get the size of the application window
        window_size = self.GetSize()

        # Calculate the scaling factor to fit the image within the window while maintaining aspect ratio
        scaling_factor = min(window_size.width / pil_image.width, (window_size.height - 50) / pil_image.height)

        # Apply initial scale down if necessary
        if scaling_factor < 1.0:
            new_width = int(pil_image.width * scaling_factor)
            new_height = int(pil_image.height * scaling_factor)
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Further apply zoom scale if not equal to 1.0 (for zooming functionality)
        if self.zoom_scale != 1.0:
            new_width = int(new_width * self.zoom_scale)
            new_height = int(new_height * self.zoom_scale)
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        wx_image = wx.Image(img_byte_arr)

        self.image_control.SetBitmap(wx.Bitmap(wx_image))
        self.scroll_panel.SetVirtualSize(wx_image.GetSize())
        self.scroll_panel.SetScrollRate(20, 20)
        self.scroll_panel.Layout()

    def on_prev(self, event):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image()

    def on_next(self, event):
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_image()

    def on_zoom_in(self, event):
        self.zoom_scale *= 1.25  # Increase zoom level
        self.load_image()

    def on_zoom_out(self, event):
        if self.zoom_scale > 0.25:
            self.zoom_scale /= 1.25  # Decrease zoom level
            self.load_image()

if __name__ == '__main__':
    app = wx.App(False)
    frame = FloorPlanVisualizer(None, 'Floor Plan Visualizer', '/Users/nick/Desktop/esx_files/OUTPUT/blank')
    app.MainLoop()
