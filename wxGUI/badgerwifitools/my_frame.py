# my_frame.py

import wx
import os
import json
import threading
import webbrowser
import subprocess
import importlib.util
from pathlib import Path
from importlib.machinery import SourceFileLoader

from drop_target import DropTarget
from common import file_or_dir_exists

from esx_actions.validate_esx import validate_esx
from esx_actions.unpack_esx import unpack_esx_file
from esx_actions.summarise_esx import summarise_esx
from esx_actions.backup_esx import backup_esx
from esx_actions.ap_list_creator import create_ap_list
from esx_actions.display_project_details import display_project_details
from esx_actions.rebundle_esx import rebundle_project

from rename_aps._visualiser import visualise_ap_renaming

from exports import export_ap_images

from docx_manipulation.insert_images import insert_images_threaded
from docx_manipulation.docx_to_pdf import convert_docx_to_pdf_threaded

from map_creator.extract_blank_maps import extract_blank_maps
from map_creator.create_custom_ap_location_maps import create_custom_ap_location_maps_threaded
from map_creator.create_zoomed_ap_location_maps import create_zoomed_ap_location_maps_threaded
from map_creator.create_pds_maps import create_pds_maps_threaded

from rename_aps._ap_renamer import ap_renamer


# CONSTANTS
from common import nl
from common import DOCX_EXTENSION
from common import CONFIGURATION_DIR
from common import PROJECT_PROFILES_DIR
from common import RENAME_APS_DIR
from common import discover_available_scripts


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1000, 800))
        self.SetMinSize((800, 600))
        self.panel = wx.Panel(self)
        self.initialize_variables()
        self.setup_list_box()
        self.setup_display_log()
        self.setup_tabs()
        self.setup_text_labels()
        self.setup_buttons()
        self.setup_dropdowns()
        self.setup_text_input_boxes()
        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()
        self.setup_panel_rows()
        self.setup_main_sizer()
        self.create_menu()
        self.setup_drop_target()
        self.load_application_state()
        self.Center()
        self.Show()

    def initialize_variables(self):
        self.esx_project_unpacked = False
        self.working_directory = None
        self.esx_project_unpacked = False  # Initialize the state variable
        self.working_directory = None
        self.esx_project_name = None
        self.esx_filepath = None
        self.current_project_profile_module = None
        self.esx_required_tag_keys = {}
        self.esx_optional_tag_keys = {}
        self.docx_files = []

        # Define the configuration directory path
        self.config_dir = Path(__file__).resolve().parent / CONFIGURATION_DIR

        # Ensure the configuration directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Define the path for the application state file
        self.app_state_file_path = self.config_dir / 'app_state.json'

        # Create a thread control variable
        self.stop_event = threading.Event()  # Initialize the stop event

    def setup_list_box(self):
        # Set up your list box here
        self.list_box = wx.ListBox(self.panel, style=wx.LB_EXTENDED)

        self.list_box.Bind(wx.EVT_KEY_DOWN, self.on_delete_key)

    def setup_display_log(self):
        # Setup display log here
        self.display_log = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Set a monospaced font for display_log
        monospace_font = wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.display_log.SetFont(monospace_font)

    def setup_dropdowns(self):
        """
        Setup all dropdown elements
        """
        # Discover available AP renaming scripts in 'rename_aps' directory
        self.available_ap_rename_scripts = discover_available_scripts(RENAME_APS_DIR)

        # Create a dropdown to select an AP renaming script
        self.ap_rename_script_dropdown = wx.Choice(self.tab1, choices=self.available_ap_rename_scripts)
        self.ap_rename_script_dropdown.SetSelection(0)  # Set default selection
        self.ap_rename_script_dropdown.Bind(wx.EVT_CHOICE, self.on_ap_rename_script_dropdown_selection)

        # Discover available project Profiles 'project_profiles' directory
        self.available_project_profiles = discover_available_scripts(PROJECT_PROFILES_DIR)

        # Create a dropdown to select a Project Profile
        self.project_profile_dropdown = wx.Choice(self.tab1, choices=self.available_project_profiles)
        self.project_profile_dropdown.SetSelection(0)  # Set default selection
        self.project_profile_dropdown.Bind(wx.EVT_CHOICE, self.on_project_profile_dropdown_selection)

    def setup_buttons(self):
        # Create add file button
        self.add_files_button = wx.Button(self.panel, label="Add Files")
        self.add_files_button.Bind(wx.EVT_BUTTON, self.on_add_file)
        self.add_files_button.SetToolTip(wx.ToolTip("Add .esx or .docx files to the file list"))

        # Create open working directory button
        self.open_working_directory_button = wx.Button(self.panel, label="Open Working Directory")
        self.open_working_directory_button.Bind(wx.EVT_BUTTON, self.on_open_working_directory)
        self.open_working_directory_button.SetToolTip(wx.ToolTip("Open the .esx working directory in your file manager"))

        # Create reset button
        self.reset_button = wx.Button(self.panel, label="Reset")
        self.reset_button.Bind(wx.EVT_BUTTON, self.on_reset)
        self.reset_button.SetToolTip(wx.ToolTip("Clear the file list and reset the application state"))

        # Create copy log button
        self.copy_log_button = wx.Button(self.panel, label="Copy Log")
        self.copy_log_button.Bind(wx.EVT_BUTTON, self.on_copy_log)
        self.copy_log_button.SetToolTip(wx.ToolTip("Copy the log to the clipboard"))

        # Create clear log button
        self.clear_log_button = wx.Button(self.panel, label="Clear Log")
        self.clear_log_button.Bind(wx.EVT_BUTTON, self.on_clear_log)
        self.clear_log_button.SetToolTip(wx.ToolTip("Clear the log"))

        self.display_project_detail_button = wx.Button(self.panel, label="Display Project Detail")
        self.display_project_detail_button.Bind(wx.EVT_BUTTON, self.on_display_project_detail)
        self.display_project_detail_button.SetToolTip(wx.ToolTip("Display detailed information about the current .esx project"))

        # Create unpack esx file button
        self.unpack_button = wx.Button(self.panel, label="Unpack .esx")
        self.unpack_button.Bind(wx.EVT_BUTTON, self.on_unpack)
        self.unpack_button.SetToolTip(wx.ToolTip("Unpack the selected .esx file"))

        # Create re-bundle esx file button
        self.rebundle_button = wx.Button(self.panel, label="Re-bundle .esx")
        self.rebundle_button.Bind(wx.EVT_BUTTON, self.on_rebundle_esx)
        self.rebundle_button.SetToolTip(wx.ToolTip("Re-bundle the unpacked project into a new .esx file"))

        # Create backup esx file button
        self.backup_button = wx.Button(self.panel, label="Backup .esx")
        self.backup_button.Bind(wx.EVT_BUTTON, self.on_backup)
        self.backup_button.SetToolTip(wx.ToolTip("Make a backup the of .esx file currently in the file list"))

        # Create a button to execute the selected AP renaming script
        self.rename_aps_button = wx.Button(self.tab1, label="Rename APs")
        self.rename_aps_button.Bind(wx.EVT_BUTTON, self.on_rename_aps)
        self.rename_aps_button.SetToolTip(wx.ToolTip("Execute the selected AP renaming script"))

        self.visualise_ap_renaming_button = wx.Button(self.tab1, label="AP Rename Visualiser")
        self.visualise_ap_renaming_button.Bind(wx.EVT_BUTTON, self.on_visualise_ap_renaming)
        self.visualise_ap_renaming_button.SetToolTip(wx.ToolTip("Preview the AP renaming results"))

        # Create a button for showing long descriptions with a specified narrow size
        self.description_button = wx.Button(self.tab1, label="?", size=(20, -1))  # Width of 40, default height
        self.description_button.Bind(wx.EVT_BUTTON, self.on_description_button_click)
        self.description_button.SetToolTip(wx.ToolTip("Show long description of the selected AP renaming script"))

        # Create a button to create an AP List Excel file in accordance with the selected project profile
        self.create_ap_list = wx.Button(self.tab1, label="AP List")
        self.create_ap_list.Bind(wx.EVT_BUTTON, self.on_create_ap_list)
        self.create_ap_list.SetToolTip(wx.ToolTip("Export AP data to Excel in accordance with the selected project profile"))

        self.validate_button = wx.Button(self.tab1, label="Validate")
        self.validate_button.Bind(wx.EVT_BUTTON, self.on_validate)
        self.validate_button.SetToolTip(wx.ToolTip("Validate the .esx project in accordance with the selected project profile"))

        self.summarise_button = wx.Button(self.tab1, label="Summarise")
        self.summarise_button.Bind(wx.EVT_BUTTON, self.on_summarise)
        self.summarise_button.SetToolTip(wx.ToolTip("Summarise the contents of the .esx project"))

        self.export_ap_images_button = wx.Button(self.tab2, label="AP Images")
        self.export_ap_images_button.Bind(wx.EVT_BUTTON, self.on_export_ap_images)
        self.export_ap_images_button.SetToolTip(wx.ToolTip("Images from within AP notes"))

        self.export_note_images_button = wx.Button(self.tab2, label="Note Images")
        self.export_note_images_button.Bind(wx.EVT_BUTTON, self.on_export_note_images)
        self.export_note_images_button.SetToolTip(wx.ToolTip("Images from within map notes"))

        self.extract_blank_maps_button = wx.Button(self.tab2, label="Blank Maps")
        self.extract_blank_maps_button.Bind(wx.EVT_BUTTON, self.on_export_blank_maps)
        self.extract_blank_maps_button.SetToolTip(wx.ToolTip("No APs, no walls, nothing, just the map image as it was imported"))

        self.create_ap_location_maps_button = wx.Button(self.tab2, label="AP Location Maps")
        self.create_ap_location_maps_button.Bind(wx.EVT_BUTTON, self.on_create_ap_location_maps)
        self.create_ap_location_maps_button.SetToolTip(wx.ToolTip("Generate AP location maps with custom AP icons"))

        self.create_zoomed_ap_maps_button = wx.Button(self.tab2, label="Zoomed AP Maps")
        self.create_zoomed_ap_maps_button.Bind(wx.EVT_BUTTON, self.on_create_zoomed_ap_maps)
        self.create_zoomed_ap_maps_button.SetToolTip(wx.ToolTip("Generate zoomed per AP location maps with custom AP icons"))

        self.export_pds_maps_button = wx.Button(self.tab2, label="PDS Maps")
        self.export_pds_maps_button.Bind(wx.EVT_BUTTON, self.on_export_pds_maps)
        self.export_pds_maps_button.SetToolTip(wx.ToolTip("Generate maps with red circle AP markers for use during Post Deployment Surveys"))

        self.insert_images_button = wx.Button(self.tab3, label="Insert Images to .docx")
        self.insert_images_button.Bind(wx.EVT_BUTTON, self.on_insert_images)
        self.insert_images_button.SetToolTip(wx.ToolTip("Perform image insertion and text string replacement for .docx file(s)"))

        self.convert_docx_to_pdf_button = wx.Button(self.tab3, label="Convert .docx to PDF")
        self.convert_docx_to_pdf_button.Bind(wx.EVT_BUTTON, self.on_convert_docx_to_pdf)
        self.convert_docx_to_pdf_button.SetToolTip(wx.ToolTip("Convert .docx file(s) to PDF"))

        # Create an abort thread button
        self.abort_thread_button = wx.Button(self.panel, label="Abort Current Process")
        self.abort_thread_button.Bind(wx.EVT_BUTTON, self.on_abort_thread)

        # Create exit button
        self.exit_button = wx.Button(self.panel, label="Exit")
        self.exit_button.Bind(wx.EVT_BUTTON, self.on_exit)

    def setup_text_input_boxes(self):
        # Create a text input box for the zoomed AP image crop size
        self.zoomed_ap_crop_text_box = wx.TextCtrl(self.tab2, value="2000", style=wx.TE_PROCESS_ENTER)

        # Create a text input box for the custom AP icon size
        self.custom_ap_icon_size_text_box = wx.TextCtrl(self.tab2, value="50", style=wx.TE_PROCESS_ENTER)

    def setup_text_labels(self):
        # Create a text label for the drop target with custom position
        self.drop_target_label = wx.StaticText(self.panel, label="Drag and Drop files here", pos=(22, 17))

        # Create a text label for the AP renaming script dropdown
        self.ap_rename_script_label = wx.StaticText(self.tab1, label="Rename APs:")

        # Create a text label for the Project Profile dropdown
        self.project_profile_label = wx.StaticText(self.tab1, label="Project Profile:")

        # Create a text label for the Create AP List function
        self.create_ap_list_label = wx.StaticText(self.tab1, label="Export to Excel:")

        # Create a text label for the Create Custom AP Map functions
        self.create_custom_ap_map_label = wx.StaticText(self.tab2, label="Create Custom:")

        # Create a text label for the zoomed AP crop size text box
        self.zoomed_ap_crop_label = wx.StaticText(self.tab2, label="Zoomed AP Crop Size:")
        self.zoomed_ap_crop_label.SetToolTip(wx.ToolTip("Enter the size of the zoomed AP crop in pixels"))

        # Create a text label for the custom AP icon size
        self.custom_ap_icon_size_label = wx.StaticText(self.tab2, label="Custom AP Icon Size:")
        self.custom_ap_icon_size_label.SetToolTip(wx.ToolTip("Enter the size of the custom AP icon in pixels"))

        # Create a text label for Export functions
        self.export_label = wx.StaticText(self.tab2, label="Export:")

    def setup_panel_rows(self):
        self.button_row1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_row1_sizer.Add(self.add_files_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.button_row1_sizer.AddStretchSpacer(1)
        self.button_row1_sizer.Add(self.open_working_directory_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.button_row1_sizer.Add(self.reset_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        self.button_row2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_row2_sizer.Add(self.copy_log_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.button_row2_sizer.Add(self.clear_log_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.button_row2_sizer.AddStretchSpacer(1)
        self.button_row2_sizer.Add(self.display_project_detail_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.button_row2_sizer.Add(self.unpack_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.button_row2_sizer.Add(self.rebundle_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.button_row2_sizer.Add(self.backup_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        self.button_exit_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_exit_row_sizer.AddStretchSpacer(1)
        self.button_exit_row_sizer.Add(self.abort_thread_button, 0, wx.ALL, 5)
        self.button_exit_row_sizer.Add(self.exit_button, 0, wx.ALL, 5)

    def setup_main_sizer(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.list_box, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.button_row1_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        main_sizer.Add(self.display_log, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.button_row2_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.notebook, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.button_exit_row_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.panel.SetSizer(main_sizer)

    def setup_tabs(self):
        self.notebook = wx.Notebook(self.panel)
        self.tab1 = wx.Panel(self.notebook)
        self.tab2 = wx.Panel(self.notebook)
        self.tab3 = wx.Panel(self.notebook)

        self.notebook.AddPage(self.tab1, "Predictive Design")
        self.notebook.AddPage(self.tab2, "Asset Creator")
        self.notebook.AddPage(self.tab3, "DOCX")

        self.tab1_sizer = wx.BoxSizer(wx.VERTICAL)
        self.tab2_sizer = wx.BoxSizer(wx.VERTICAL)
        self.tab3_sizer = wx.BoxSizer(wx.VERTICAL)

        # Bind the tab change event
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_changed)

    def setup_tab1(self):
        self.tab1_row1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tab1_row1_sizer.AddStretchSpacer(1)
        self.tab1_row1_sizer.Add(self.project_profile_label, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        self.tab1_row1_sizer.Add(self.project_profile_dropdown, 0, wx.EXPAND | wx.ALL, 5)
        self.tab1_row1_sizer.Add(self.validate_button, 0, wx.ALL, 5)
        self.tab1_row1_sizer.Add(self.summarise_button, 0, wx.ALL, 5)
        self.tab1_sizer.Add(self.tab1_row1_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.tab1_row2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tab1_row2_sizer.Add(self.visualise_ap_renaming_button, 0, wx.ALL, 5)
        self.tab1_row2_sizer.AddStretchSpacer(1)
        self.tab1_row2_sizer.Add(self.ap_rename_script_label, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        self.tab1_row2_sizer.Add(self.ap_rename_script_dropdown, 0, wx.EXPAND | wx.ALL, 5)
        self.tab1_row2_sizer.Add(self.description_button, 0, wx.EXPAND | wx.ALL, 5)
        self.tab1_row2_sizer.Add(self.rename_aps_button, 0, wx.ALL, 5)
        self.tab1_sizer.Add(self.tab1_row2_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.tab1_row3_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tab1_row3_sizer.AddStretchSpacer(1)
        self.tab1_row3_sizer.Add(self.create_ap_list_label, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        self.tab1_row3_sizer.Add(self.create_ap_list, 0, wx.ALL, 5)
        self.tab1_sizer.Add(self.tab1_row3_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.tab1.SetSizer(self.tab1_sizer)

    def setup_tab2(self):
        self.tab2_row1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tab2_row1_sizer.AddStretchSpacer(1)
        self.tab2_row1_sizer.Add(self.export_label, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        self.tab2_row1_sizer.Add(self.export_ap_images_button, 0, wx.ALL, 5)
        self.tab2_row1_sizer.Add(self.export_note_images_button, 0, wx.ALL, 5)
        self.tab2_row1_sizer.Add(self.extract_blank_maps_button, 0, wx.ALL, 5)
        self.tab2_sizer.Add(self.tab2_row1_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.tab2_row2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tab2_row2_sizer.AddStretchSpacer(1)
        self.tab2_row2_sizer.AddSpacer(2)
        self.tab2_row2_sizer.Add(self.create_custom_ap_map_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.tab2_row2_sizer.Add(self.create_ap_location_maps_button, 0, wx.ALL, 5)
        self.tab2_row2_sizer.Add(self.create_zoomed_ap_maps_button, 0, wx.ALL, 5)
        self.tab2_row2_sizer.Add(self.export_pds_maps_button, 0, wx.ALL, 5)
        self.tab2_sizer.Add(self.tab2_row2_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.tab2_row3_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tab2_row3_sizer.AddStretchSpacer(1)
        self.tab2_row3_sizer.Add(self.custom_ap_icon_size_label, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        self.tab2_row3_sizer.Add(self.custom_ap_icon_size_text_box, 0, wx.EXPAND | wx.ALL, 5)
        self.tab2_row3_sizer.Add(self.zoomed_ap_crop_label, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        self.tab2_row3_sizer.Add(self.zoomed_ap_crop_text_box, 0, wx.EXPAND | wx.ALL, 5)
        self.tab2_sizer.Add(self.tab2_row3_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.tab2.SetSizer(self.tab2_sizer)

    def setup_tab3(self):
        self.tab3_row1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tab3_row1_sizer.AddStretchSpacer(1)
        self.tab3_row1_sizer.Add(self.insert_images_button, 0, wx.ALL, 5)
        self.tab3_row1_sizer.Add(self.convert_docx_to_pdf_button, 0, wx.ALL, 5)
        self.tab3_sizer.Add(self.tab3_row1_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.tab3.SetSizer(self.tab3_sizer)

    def create_menu(self):
        menubar = wx.MenuBar()

        # File Menu
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_ADD, "&Add Files", "Add files to the list")
        file_menu.Append(wx.ID_SAVE, "&Save", "Save the current configuration")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "&Exit", "Exit the application")
        menubar.Append(file_menu, "&File")

        # Help Menu
        help_menu = wx.Menu()
        contribute_menu_item = help_menu.Append(wx.ID_ANY, "&Contribute", "Go to the ko-fi contribution page")
        documentation_menu_item = help_menu.Append(wx.ID_ANY, "&Documentation", "View the documentation")
        view_release_notes_menu_item = help_menu.Append(wx.ID_ANY, "&View 'Release Notes'", "View the GitHub commit messages")
        help_menu.Append(wx.ID_ABOUT, '&About')
        menubar.Append(help_menu, '&Help')

        self.SetMenuBar(menubar)

        # Bind the menu items to their respective functions
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_add_file, id=wx.ID_ADD)
        self.Bind(wx.EVT_MENU, self.on_save, id=wx.ID_SAVE)

        self.Bind(wx.EVT_MENU, self.on_contribute, contribute_menu_item)
        self.Bind(wx.EVT_MENU, self.on_view_documentation, documentation_menu_item)
        self.Bind(wx.EVT_MENU, self.on_view_release_notes, view_release_notes_menu_item)


    @staticmethod
    def on_contribute(event):
        webbrowser.open("https://ko-fi.com/badgerwifitools")

    @staticmethod
    def on_view_documentation(event):
        webbrowser.open("https://badgerwifi.co.uk")

    @staticmethod
    def on_view_release_notes(event):
        webbrowser.open("https://github.com/nickjvturner/badgerwifi-git/activity")

    @staticmethod
    def on_about(event):
        # Implement the About dialog logic
        wx.MessageBox("This is a wxPython GUI application created by Nick Turner. Intended to make the lives of Wi-Fi engineers making reports a little bit easier. ", "About")

    def on_save(self, event):
        self.save_application_state(event)
        message = f'Application state saved on exit, file list and dropdown options should be the same next time you launch the app.'
        self.append_message(message)
        print(message)

    def setup_drop_target(self):
        """Set up the drop target for the list box."""
        allowed_extensions = (".esx", ".docx", ".xlsx")  # Define allowed file extensions
        drop_target = DropTarget(self.list_box, allowed_extensions, self.append_message, self.esx_project_unpacked, self.update_esx_project_unpacked, self.drop_target_label_callback)
        self.list_box.SetDropTarget(drop_target)

    def append_message(self, message):
        # Append a message to the message display area.
        self.display_log.AppendText(message + '\n')

    def update_last_message(self, message):
        content = self.display_log.GetValue()

        # Find the last occurrence of a newline character
        last_newline_index = content.rfind('\n')

        # If there's at least one newline, replace the text after the last newline
        if last_newline_index != -1:
            # Calculate the start position for replacement (after the newline character)
            start_pos = last_newline_index + 1  # Start replacing after the newline

            # Use Replace method to replace the last line
            self.display_log.Replace(start_pos, self.display_log.GetLastPosition(), message)
        else:
            # If there's no newline, this means there's only one line, so we can directly set the value
            self.display_log.SetValue(message)

    def save_application_state(self, event):
        """Save the application state to the defined path."""
        state = {
            'list_box_contents': [self.list_box.GetString(i) for i in range(self.list_box.GetCount())],
            'selected_ap_rename_script_index': self.ap_rename_script_dropdown.GetSelection(),
            'selected_project_profile_index': self.project_profile_dropdown.GetSelection(),
            'selected_tab_index': self.notebook.GetSelection(),
            'custom_ap_icon_size_text_box': self.custom_ap_icon_size_text_box.GetValue(),
            'zoomed_ap_crop_text_box': self.zoomed_ap_crop_text_box.GetValue()
        }
        # Save the state to the defined path
        with open(self.app_state_file_path, 'w') as f:
            json.dump(state, f)

    def load_application_state(self):
        """Load the application state from the defined path."""
        try:
            with open(self.app_state_file_path, 'r') as f:
                state = json.load(f)
                # Restore list box contents
                for item in state.get('list_box_contents', []):
                    if not file_or_dir_exists(item):
                        self.append_message(f"** WARNING ** {nl}The file {item} does not exist.")
                    self.list_box.Append(item)
                    self.drop_target_label.Hide()  # Hide the drop target label
                # Restore selected ap rename script index
                self.ap_rename_script_dropdown.SetSelection(state.get('selected_ap_rename_script_index', 0))
                self.on_ap_rename_script_dropdown_selection(None)
                # Restore selected project profile index
                self.project_profile_dropdown.SetSelection(state.get('selected_project_profile_index', 0))
                self.on_project_profile_dropdown_selection(None)
                # Restore selected tab index
                self.notebook.SetSelection(state.get('selected_tab_index', 0))
                # Restore the text box values
                self.custom_ap_icon_size_text_box.SetValue(state.get('custom_ap_icon_size_text_box', "50"))
                self.zoomed_ap_crop_text_box.SetValue(state.get('zoomed_ap_crop_text_box', "2000"))
        except FileNotFoundError:
            self.on_ap_rename_script_dropdown_selection(None)
            self.on_project_profile_dropdown_selection(None)
            pass  # It's okay if the state file doesn't exist on first run

    def on_reset(self, event):
        self.list_box.Clear()  # Reset list_box contents
        self.display_log.SetValue("")  # Clear the contents of the display_log
        self.esx_project_unpacked = False  # Reset project_unpacked state
        self.drop_target_label.Show()  # Show the drop target label
        self.custom_ap_icon_size_text_box.SetValue("50")  # Reset the custom AP icon size
        self.zoomed_ap_crop_text_box.SetValue("2000")  # Reset the zoomed AP crop size
        self.stop_event.clear()  # Clear the stop event

    def on_clear_log(self, event):
        self.display_log.SetValue("")  # Clear the contents of the display_log

    def on_add_file(self, event):
        existing_files = self.list_box.GetStrings()  # Get currently listed files

        wildcard = "Ekahau Project file (*.esx)|*.esx|Microsoft Word document (*.docx)|*.docx"
        dlg = wx.FileDialog(self, "Choose a file", wildcard=wildcard,
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            filepaths = dlg.GetPaths()
            for filepath in filepaths:
                if "re-zip" in filepath:
                    self.append_message(f"{Path(filepath).name} cannot be added because it contains 're-zip' in the name.")
                    continue

                if filepath in existing_files:
                    self.append_message(f"{Path(filepath).name} is already in the list.")
                    continue

                if filepath.lower().endswith('.esx'):
                    # Initialize a flag to track if the .esx file is replaced or added
                    existing_esx_in_list = False

                    # Check if there is an existing .esx file in the list
                    for index, existing_file in enumerate(existing_files):
                        if existing_file.lower().endswith('.esx'):
                            # There is already an .esx file in the list, show replace dialog
                            existing_esx_in_list = True  # Mark the file as processed
                            if not Path(existing_file).exists():
                                self.list_box.Delete(index)  # Remove the existing .esx file
                                self.list_box.Append(filepath)  # Append the new one
                                self.append_message(f'{existing_file} replaced with {filepath}')
                                self.esx_project_unpacked = False

                            elif self.show_replace_dialog(filepath):
                                self.append_message(f"{Path(self.list_box.GetStrings()[0]).name} removed.")
                                self.list_box.Delete(index)  # Remove the existing .esx file
                                self.list_box.Append(filepath)  # Append the new one
                                self.append_message(f"{Path(filepath).name} added to the list.")
                                self.esx_project_unpacked = False

                    # If no existing .esx file was found or replacement was not approved, append the new file
                    if not existing_esx_in_list:
                        self.list_box.Append(filepath)
                        self.append_message(f"{Path(filepath).name} added to the list.")

                if filepath.lower().endswith('.docx'):
                    self.list_box.Append(filepath)
                    self.append_message(f"{Path(filepath).name} added to the list.")

                if self.list_box.GetCount() > 0:
                    self.drop_target_label.Hide()

        dlg.Destroy()

    def on_delete_key(self, event):
        keycode = event.GetKeyCode()
        if keycode in [wx.WXK_DELETE, wx.WXK_BACK]:
            selected_indices = self.list_box.GetSelections()
            for index in reversed(selected_indices):
                self.list_box.Delete(index)

    def on_unpack(self, event):
        if not self.esx_project_unpacked:
            self.unpack_esx()
            return
        # Create a message dialog with Yes and No buttons
        dlg = wx.MessageDialog(None, "Project has already been unpacked. Would you like to re-unpack it?",
                               "Re-unpack project?", wx.YES_NO | wx.ICON_QUESTION)
        # Show the dialog and check the response
        result = dlg.ShowModal()

        if result == wx.ID_YES:
            # User wants to re-unpack the project
            self.esx_project_unpacked = False
            self.unpack_esx()
        else:
            # User chose not to re-unpack the project
            self.append_message(f"Re-unpack operation aborted{nl}")
        # Destroy the dialog after using it
        dlg.Destroy()

    def on_backup(self, event):
        if not self.esx_filepath:
            if not self.get_single_specific_file_type('.esx'):
                return
        backup_esx(self.working_directory, self.esx_project_name, self.esx_filepath, self.append_message)

    def on_validate(self, event):
        if not self.basic_checks():
            return
        validate_esx(self.working_directory, self.esx_project_name, self.append_message, self.esx_required_tag_keys, self.esx_optional_tag_keys)

    def on_summarise(self, event):
        if not self.basic_checks():
            return
        summarise_esx(self.working_directory, self.esx_project_name, self.append_message)

    def on_create_ap_list(self, event):
        if not self.basic_checks():
            return
        if hasattr(self, 'current_project_profile_module'):
            create_ap_list(self.working_directory, self.esx_project_name, self.append_message, self.current_profile_ap_list_module.create_custom_ap_list)

    def on_copy_log(self, event):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.display_log.GetValue()))
            wx.TheClipboard.Close()
            self.append_message("Log copied to clipboard.")
        else:
            wx.MessageBox("Unable to access the clipboard.", "Error", wx.OK | wx.ICON_ERROR)

    def on_exit(self, event):
        # Save the application state before exiting
        self.save_application_state(None)
        print(f'Application state saved on exit, file list and dropdown options should be the same next time you launch the application')
        self.Close()
        self.Destroy()

    def get_multiple_specific_file_type(self, extension):
        filepaths = []
        for filepath in self.list_box.GetStrings():
            if filepath.lower().endswith(extension):
                filepaths.append(filepath)

        if filepaths:
            return filepaths

        self.append_message(f"No file with {extension} present in file list.")
        return None

    def get_single_specific_file_type(self, extension):
        for filepath in self.list_box.GetStrings():
            if filepath.lower().endswith(extension):
                if extension == '.esx':
                    self.esx_filepath = Path(filepath)
                    if not self.esx_filepath.exists():
                        self.append_message(f'The file {self.esx_filepath} does not exist.')
                        return False
                    self.esx_project_name = self.esx_filepath.stem  # Set the project name based on the file stem
                    self.append_message(f'Project name: {self.esx_project_name}')
                    self.working_directory = self.esx_filepath.parent
                    self.append_message(f'Working directory: {self.working_directory}{nl}')
                return True

        self.append_message(f"No file with {extension} present in file list.")
        return False

    def unpack_esx(self):
        if not self.esx_project_unpacked:
            if not self.get_single_specific_file_type('.esx'):
                return
            unpack_esx_file(self.working_directory, self.esx_project_name, self.esx_filepath, self.append_message)
            self.esx_project_unpacked = True
        return True

    def load_project_profile(self, profile_name):
        profile_path = Path(__file__).resolve().parent / "project_profiles" / f"{profile_name}.py"
        spec = importlib.util.spec_from_file_location(profile_name, str(profile_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def on_project_profile_dropdown_selection(self, event):
        selected_profile = self.project_profile_dropdown.GetStringSelection()
        project_profile_module = self.load_project_profile(selected_profile)
        self.current_profile_ap_list_module = project_profile_module

        # Update the object variables with the configuration from the selected module
        self.esx_required_tag_keys = getattr(project_profile_module, 'requiredTagKeys', None)
        self.esx_optional_tag_keys = getattr(project_profile_module, 'optionalTagKeys', None)
        self.save_application_state(None)

    def on_rename_aps(self, event):
        if not self.basic_checks():
            return
        selected_script = self.available_ap_rename_scripts[self.ap_rename_script_dropdown.GetSelection()]
        script_path = str(Path(__file__).resolve().parent / RENAME_APS_DIR / (selected_script + ".py"))

        # Load and execute the selected script
        script_module = SourceFileLoader(selected_script, script_path).load_module()
        if hasattr(script_module, 'SAR'):
            script_module.run(self.working_directory, self.esx_project_name, self.append_message)
        else:
            ap_renamer(self.working_directory, self.esx_project_name, script_module.sort_logic, self.append_message)

    def on_ap_rename_script_dropdown_selection(self, event):
        selected_script = self.available_ap_rename_scripts[self.ap_rename_script_dropdown.GetSelection()]
        _, short_description, _ = self.get_ap_rename_script_descriptions(selected_script)  # Ignore script_name and long_description
        self.ap_rename_script_dropdown.SetToolTip(wx.ToolTip(short_description))
        self.save_application_state(None)

    def get_ap_rename_script_descriptions(self, script_name):
        script_path = str(Path(__file__).resolve().parent / "rename_aps" / f"{script_name}.py")
        spec = importlib.util.spec_from_file_location(script_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        short_description = getattr(module, 'SHORT_DESCRIPTION', "No short description available.")
        long_description = getattr(module, 'LONG_DESCRIPTION', "No long description available.")
        return script_name, short_description, long_description

    def on_description_button_click(self, event):
        selected_script = self.available_ap_rename_scripts[self.ap_rename_script_dropdown.GetSelection()]
        script_name, short_description, long_description = self.get_ap_rename_script_descriptions(selected_script)
        self.show_long_description_dialog(script_name, long_description)

    def show_long_description_dialog(self, script_name, long_description):
        # Create a dialog with a resize border
        dialog = wx.Dialog(self, title=f"{script_name} Long Description", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        # Create a sizer for the dialog content
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add a text control with a minimum size set
        text_ctrl = wx.TextCtrl(dialog, value=long_description, style=wx.TE_MULTILINE | wx.TE_READONLY)
        text_ctrl.SetMinSize((580, 350))  # Adjust the minimum size if needed
        dialog_sizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 10)

        # Add a dismiss button
        dismiss_button = wx.Button(dialog, label="Dismiss")
        dialog_sizer.Add(dismiss_button, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        dismiss_button.Bind(wx.EVT_BUTTON, lambda event: dialog.EndModal(wx.ID_OK))

        # Apply the sizer to the dialog. This adjusts the dialog to fit the sizer's content.
        dialog.SetSizer(dialog_sizer)

        # Explicitly set the dialog's size after applying the sizer to ensure it's not just limited to the sizer's minimum size
        dialog.SetSize((800, 400))

        # Optionally, you can set a minimum size for the dialog to ensure it cannot be resized smaller than desired
        dialog.SetMinSize((600, 400))

        dialog.ShowModal()
        dialog.Destroy()

    def update_esx_project_unpacked(self, unpacked):
        self.esx_project_unpacked = unpacked

    def placeholder(self, event):
        self.append_message(f'No action implemented yet')

    def on_export_ap_images(self, event):
        if not self.basic_checks():
            return
        export_ap_images.export_ap_images(self.working_directory, self.esx_project_name, self.append_message)

    def on_insert_images(self, event):
        docx_files = self.get_multiple_specific_file_type(DOCX_EXTENSION)
        self.stop_event.clear()
        if docx_files:
            for file in docx_files:
                insert_images_threaded(file, self.append_message, self.update_last_message, self.stop_event)

    def on_convert_docx_to_pdf(self, event):
        docx_files = self.get_multiple_specific_file_type(DOCX_EXTENSION)
        self.stop_event.clear()
        if docx_files:
            for file in docx_files:
                if self.stop_event.is_set():
                    wx.CallAfter(self.append_message, f'{nl}### PROCESS ABORTED ###')
                    return
                convert_docx_to_pdf_threaded(file, self.append_message)

    def on_export_note_images(self, event):
        self.placeholder(None)

    def on_export_pds_maps(self, event):
        if not self.basic_checks():
            return

        # Retrieve the number from the custom AP icon size text box
        custom_ap_icon_size = self.custom_ap_icon_size_text_box.GetValue()

        # Clear the stop event flag before starting the thread
        self.stop_event.clear()

        try:
            custom_ap_icon_size = int(custom_ap_icon_size)  # Convert the input to a float
            create_pds_maps_threaded(self.working_directory, self.esx_project_name, self.append_message, custom_ap_icon_size, self.stop_event)

        except ValueError:
            # Handle the case where the input is not a valid number
            wx.MessageBox("Please enter a valid number", "Error", wx.OK | wx.ICON_ERROR)

    def on_create_ap_location_maps(self, event):
        if not self.basic_checks():
            return

        # Retrieve the number from the custom AP icon size text box
        custom_ap_icon_size = self.custom_ap_icon_size_text_box.GetValue()

        # Clear the stop event flag before starting the thread
        self.stop_event.clear()

        try:
            custom_ap_icon_size = int(custom_ap_icon_size)  # Convert the input to a float
            create_custom_ap_location_maps_threaded(self.working_directory, self.esx_project_name, self.append_message, custom_ap_icon_size, self.stop_event)

        except ValueError:
            # Handle the case where the input is not a valid number
            wx.MessageBox("Please enter a valid number", "Error", wx.OK | wx.ICON_ERROR)

    def on_create_zoomed_ap_maps(self, event):
        if not self.basic_checks():
            return

        self.stop_event.clear()

        # Retrieve the number from the zoomed AP crop size text box
        zoomed_ap_crop_size = self.zoomed_ap_crop_text_box.GetValue()
        custom_ap_icon_size = self.custom_ap_icon_size_text_box.GetValue()

        try:
            zoomed_ap_crop_size = int(zoomed_ap_crop_size)  # Convert the input to a float
            custom_ap_icon_size = int(custom_ap_icon_size)  # Convert the input to a float
            create_zoomed_ap_location_maps_threaded(self.working_directory, self.esx_project_name, self.append_message, zoomed_ap_crop_size, custom_ap_icon_size, self.stop_event)
        except ValueError:
            # Handle the case where the input is not a valid number
            wx.MessageBox("Please enter a valid number", "Error", wx.OK | wx.ICON_ERROR)

    def on_export_blank_maps(self, event):
        if not self.basic_checks():
            return
        extract_blank_maps(self.working_directory, self.esx_project_name, self.append_message)

    def on_tab_changed(self, event):
        # Get the index of the newly selected tab
        self.save_application_state(None)
        # new_tab_index = event.GetSelection()
        # print(f"Tab changed to index {new_tab_index}")

        # It's important to call event.Skip() to ensure the event is not blocked
        event.Skip()

    def on_display_project_detail(self, event):
        if not self.basic_checks():
            return
        display_project_details(self.working_directory, self.esx_project_name, self.append_message)

    def on_rebundle_esx(self, event):
        if not self.esx_project_unpacked:
            self.get_single_specific_file_type('.esx')
        # Check that working directory and project name directories exist
        if self.working_directory and (self.working_directory / self.esx_project_name).exists():
            rebundle_project(self.working_directory, self.esx_project_name, self.append_message)

    def drop_target_label_callback(self, hide=False):
        if hide:
            self.drop_target_label.Hide()
        else:
            self.drop_target_label.Show()
        self.panel.Refresh()  # Refresh the panel to reflect the change

    def basic_checks(self):
        if not self.esx_project_unpacked:
            if not self.unpack_esx():
                return False
        self.on_clear_log(None)
        return True

    def on_abort_thread(self, event):
        self.stop_event.set()

    def on_open_working_directory(self, event):
        if not self.esx_project_unpacked:
            self.append_message("Project has not been unpacked yet, the working directory is not defined.")
            return
        try:
            # Open the directory using the operating system's file navigator
            if os.name == 'nt':  # Windows
                os.startfile(self.working_directory)
            elif os.name == 'posix':  # macOS or Linux
                # Directly attempt to use 'open' on macOS
                subprocess.Popen(['open', self.working_directory], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            wx.MessageBox(f"Error opening directory: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    def show_replace_dialog(self, filepath):
        # Dialog asking if the user wants to replace the existing .esx file
        dlg = wx.MessageDialog(self.panel,
                               f"A .esx file is already present. Do you want to replace it with {Path(filepath).name}?",
                               "Replace File?", wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        return result

    def on_visualise_ap_renaming(self, event):
        if not self.basic_checks():
            return
        visualise_ap_renaming(self.working_directory, self.esx_project_name, self.append_message, self)
