from PIL import Image
import io
import wx
from pathlib import Path


class FloorPlanVisualizer(wx.Frame):
    def __init__(self, parent, title, image_folder):
        super(FloorPlanVisualizer, self).__init__(parent, title=title, size=(800, 600))
        self.image_folder = Path(image_folder)
        self.image_files = [png for png in self.image_folder.iterdir() if png.suffix == '.png']
        self.current_image_index = 0

        self.init_ui()
        self.Center()
        self.Show()

    def init_ui(self):
        self.panel = wx.Panel(self)
        self.image_control = wx.StaticBitmap(self.panel)
        self.load_image()

        # Navigation buttons
        prev_button = wx.Button(self.panel, label='Previous', pos=(10, 530))
        next_button = wx.Button(self.panel, label='Next', pos=(690, 530))

        prev_button.Bind(wx.EVT_BUTTON, self.on_prev)
        next_button.Bind(wx.EVT_BUTTON, self.on_next)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.image_control, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(sizer)

    def load_image(self):
        if not self.image_files:  # Check if the list is empty
            return  # Exit the function if there are no images to display

        filepath = self.image_files[self.current_image_index]

        pil_image = Image.open(filepath).convert("RGB")
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)  # Important: seek to the start of the BytesIO buffer

        wx_image = wx.Image(img_byte_arr)
        W, H = self.GetSize().width, self.GetSize().height - 50  # Adjust height for control buttons
        wx_image = wx_image.Scale(W, H, wx.IMAGE_QUALITY_HIGH)

        self.image_control.SetBitmap(wx.Bitmap(wx_image))
        self.panel.Layout()

    def on_prev(self, event):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image()

    def on_next(self, event):
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_image()


if __name__ == '__main__':
    app = wx.App(False)
    frame = FloorPlanVisualizer(None, 'Floor Plan Visualizer', '/Users/nick/Desktop/esx_files/Odense')
    app.MainLoop()
