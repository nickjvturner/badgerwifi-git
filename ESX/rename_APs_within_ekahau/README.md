# rename_APs
## Instructions for Use

Place A **COPY** of your project file into the same directory as the python script.

1. Navigate to the folder in your Terminal
2. Execute the python script
3. It should automatically find the project file (.esx)
4. Hit Enter to proceed
5. The project file will be unpacked into a folder with the same name as the .esx file
6. The file accessPoints.json is loaded and modified
7. ALL APs in the project across all floors and buildings will be renamed
   1. The sorting prioity may be altered
   2. 'default / initial' sorting priority:
      1. floor name
      2. specific sorting tag
      3. model of AP
      4. X co-ordinate numbered from left to right
   3. APs will be numbered incrementally according to a naming pattern
   4. 'default / initial' naming pattern:
      5. AP-XXX
8. The modified files are saved, overwriting the original
9. Directory is zipped back up again into 'theoretically' a functional **NEW** .esx project file
   10. original_project_name_re-zip.esx
