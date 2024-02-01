# rename_APs Scripts
## Instructions for Use

Place A **COPY** of your project file into the same directory as the python script.

1. Navigate to the folder in your Terminal
2. Execute the python script
3. The script should:
     * Automatically find the project file (.esx)
     * Note that filenames containing *re-zip* will be ignored
4. Prompt in terminal window will ask you to confirm that you wish to proceed with the discovered .esx file
5. Hit Enter to proceed
6. The project file will be unpacked into a folder with the same name as the .esx file
7. The file accessPoints.json file is loaded
8. The APs will essentially be added to a Python list and depending on the script file you execute this list will be sorted according to various criteria
9. Once sorted, the APs will be sequentially renamed according to the naming pattern defined in the script
10. Take a look at the comments at the top of each .py script to understand what each script attempts to do
11. Once the modification is complete the modified files are saved
12. The directory is zipped back up again, into 'theoretically', a functional **NEW** .esx project file with file name *original_project_name_re-zip.esx*
