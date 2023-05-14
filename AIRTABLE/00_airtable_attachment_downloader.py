#!/usr/bin/env python3

"""
Created by Nick Turner (@nickjvturner)


"""
import pandas as pd
import requests
import re
import os
import csv
import requests
from pathlib import Path

nl = '\n'

# create a directory for the images
if not os.path.exists("AP images"):
    os.mkdir("AP images")

# Get filename and current working directory
print(f'{nl}{Path(__file__).name}')
print(f'working_directory: {Path.cwd()}{nl}')

# Get local file with extension .esx
for file in sorted(Path.cwd().iterdir()):
    # ignore files in directory containing _re-zip
    if file.suffix == '.csv':
        proceed = input(f'Proceed with file: {str(file.name)}? (YES/no)')
        if proceed == 'no':
            continue

        print('filename:', file.name)

        # Define the project name
        project_name = file.stem
        print('project_name:', project_name)


        # read the csv file into a pandas DataFrame
        df = pd.read_csv(file)

        # loop through each row in the DataFrame
        for i, row in df.iterrows():
            # extract the AP name and URLs from the row
            ap_name = row['AP Name']
            attachments = row['Attachments']
            urls = re.findall(r'\((.*?)\)', attachments)

            # download each image file and save it with the AP name as the filename
            for url in urls:
                response = requests.get(url)
                with open('AP Images/' + ap_name + '_' + str(urls.index(url)) + '.png', 'wb') as f:
                    f.write(response.content)
                    print(f'{ap_name}_{str(urls.index(url))}.png downloaded successfully')

