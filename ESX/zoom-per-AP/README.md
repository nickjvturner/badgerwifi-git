# zoom-per-AP
## Instructions for Use

Place (1x) or more of your project files into the same directory as the python script.

1. Navigate to the directory in your Terminal
2. Execute the python script
3. It should automatically find the project file (.esx)
4. Hit Enter to proceed
5. The project file will be unpacked into a folder with the same name as the .esx file


### 00_zoom-per-AP__pre-drawn_Ekahau_APs
This is the only script that requires 'input' floor plans!
1. Script will load the floorPlans.json file
2. create a new folder called 'INPUT'
3. You need to provide floor plans with APs visible and any other detail you wish
   1. do this from within Ekahau, reporting > Export Image
4. Continue with the script, Each AP on each floor plan will be zoomed in on and an individual AP image created.
5. Script will create a new directory called OUTPUT
   1. Within OUTPUT, it will create a new directory called
      1. "annotated", this folder will contain copies of the 'Ekahau' annotated floor plans
      2. "zoomed-APs", this folder will contain zoom and cropped clippings from the source maps, centered on each AP
6. The 'problem' with this script is that if the APs are close together and overlapping, there is no 'fix' because Ekahau already drew the AP icons onto the exported map. 


### 01_draw_custom_AP_icons
This script will draw custom AP icons using Python Image Library (PIL)
1. Script will create a new directory called OUTPUT
   1. Within OUTPUT, it will create a new directory called:
      1. "blank", this folder will contain blank exports of each floor plan from the Ekahau project file
      2. "annotated", this folder will contain floor plans with all of the APs marked with the custom icon


### 02_zoom-per-AP__draw_custom_icons
This script will draw custom AP icons using Python Image Library (PIL)
1. Script will create a new directory called OUTPUT
   1. Within OUTPUT, it will create a new directory called:
      1. "blank", this folder will contain blank exports of each floor plan from the Ekahau project file
      2. "annotated", this folder will contain floor plans with all of the APs marked with the custom icon
      3. "zoomed-APs", this folder will contain zoom and cropped clippings from the annotated floor plans, centered on each AP


### 03_zoom-per-AP__draw_custom_icons_plus_text
This script will draw custom AP icons and add text (the AP name) using Python Image Library (PIL)
1. Script will create a new directory called OUTPUT
   1. Within OUTPUT, it will create a new directory called:
      1. "blank", this folder will contain blank exports of each floor plan from the Ekahau project file
      2. "annotated", this folder will contain floor plans with all of the APs marked with the custom icon
      3. "zoomed-APs", this folder will contain zoom and cropped clippings from the annotated floor plans, centered on each AP


### 04_zoom-per-AP__import_custom_icons_with_AP_name
This script imports custom AP icons from the assets directory, includes text under each AP icon (AP Name)
1. Script will create a new directory called OUTPUT
   1. Within OUTPUT, it will create a new directory called:
      1. "blank", this folder will contain blank exports of each floor plan from the Ekahau project file
      2. "annotated", this folder will contain floor plans with all of the APs marked with the custom icon
      3. "zoomed-APs", this folder will contain zoom and cropped clippings from the annotated floor plans, centered on each AP


### 05_zoom-per-AP__import_custom_icons_plus_additional_text
This script imports custom AP icons from the assets directory, includes text box in upper right corner of export
1. Script will create a new directory called OUTPUT
   1. Within OUTPUT, it will create a new directory called:
      1. "blank", this folder will contain blank exports of each floor plan from the Ekahau project file
      2. "annotated", this folder will contain floor plans with all of the APs marked with the custom icon
      3. "zoomed-APs", this folder will contain zoom and cropped clippings from the annotated floor plans, centered on each AP


1. This script imports custom AP icons from the assets directory
2. Moves text to the upper-right hand corner
   1. AP Name
   2. AP Vendor
   3. AP Model
   4. AP Mount
   5. AP Height
   6. Antenna Tilt
3. Script will create a new directory called OUTPUT
   1. Within OUTPUT, it will create a new directory called:
      1. "blank", this folder will contain blank exports of each floor plan from the Ekahau project file
      2. "annotated", this folder will contain floor plans with all of the APs marked with the custom icon
      3. "zoomed-APs", this folder will contain zoom and cropped clippings from the annotated floor plans, centered on each AP
