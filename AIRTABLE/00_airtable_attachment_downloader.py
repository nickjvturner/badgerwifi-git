#!/usr/bin/env python3

"""
Created by Nick Turner (@nickjvturner@mastodon.social)

Download image files in bulk from Airtable.

The idea here, is that you created an Airtable base, each record has
at a minimum, a name field and an image attachment field, with a single image.

This script takes the 'export' from Airtable as '.csv' and pulls down the attached
image from the Airtable servers during the ~3 hour availability window, post
export.

This script can handle multiple images per record.
"""

import pandas as pd
import re
import os
import requests
from pathlib import Path
import time

nl = '\n'

record_name_column_header = 'AP Name'
image_url_column_header = 'Attachments'


def main():
    # create a directory for the images
    if not os.path.exists("AP Images"):
        os.mkdir("AP Images")

    # Get filename and current working directory
    print(f'{nl}{Path(__file__).name}')
    print(f'working_directory: {Path.cwd()}{nl}')

    # Get local file with extension .csv
    for file in sorted(Path.cwd().iterdir()):
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
                # Check if the column is not empty
                if not pd.isnull(row[image_url_column_header]):
                    # extract the AP name and URLs from the row
                    ap_name = row[record_name_column_header]
                    attachments = str(row[image_url_column_header])  # Convert to string if not already
                    urls = re.findall(r'\((http.*?)\)', attachments)

                    # download each image file and save it with the 'AP name' as the filename
                    for url in urls:
                        response = requests.get(url)
                        with open('AP Images/' + ap_name + '_' + str(urls.index(url)) + '.png', 'wb') as f:
                            f.write(response.content)
                            print(f'{ap_name}_{str(urls.index(url))}.png downloaded successfully')


if __name__ == "__main__":
    start_time = time.time()
    main()
    run_time = time.time() - start_time
    print(f'** Time to run: {round(run_time, 2)} seconds **')
