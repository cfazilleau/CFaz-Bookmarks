import requests
import os
import json
import shutil

# output dir
output_dir = "content/post/"
css_path = "static/tags.css"

# Coda.io API Details
coda_api_key = os.environ['CODA_API_KEY']

table_id = "grid-u94VwpGK6T"
doc_id = "rQ26r9zZ8-"
column_ids = {
    'title'       : 'c-XHPHS0IYDc',
    'date'        : 'c-Q3C_1Lzcky',
    'tags'        : 'c-Fj0Gs0SCy0',
    'description' : 'c-xpKHNEHbMh',
    'link'        : 'c-LQRg1noK1k',
    'image'       : 'c-_zpRcDFVkH',
}
css_backgrounds = [ '#8ea885', '#df7988', '#0177b8', '#cc9f28', '#6b69d6', '#a863c1', '#d5752f', '#62bdbd', '#ac3d3d' ]

# Define the URL for the Coda.io API
coda_api_url = f'https://coda.io/apis/v1/docs/{doc_id}/tables/{table_id}/rows'

# Headers for the Coda.io API request
headers = { 'Authorization': f'Bearer {coda_api_key}' }

# Function to fetch data from Coda.io
def fetch_data_from_coda():
    response = requests.get(coda_api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from Coda.io. Status code: {response.status_code}")
        return None

def extract_tags(data):
    tags = []
    for row in data['items']:
        for tag in row['values'][column_ids['tags']].split(','):
            tags.append(tag.replace(' ', '-'))
    tags = list(set(tags))
    print(f"Tags found ({len(tags)}): {tags}")

    print(f"Writing tag styles in {css_path}")
    with open(css_path, 'w') as file:
        file.write("html{")
        for index in range(len(css_backgrounds)):
            file.write(f"--tag-background-{index}:{css_backgrounds[index]};")
        file.write("}")
        for index in range(len(tags)):
            file.write(f".tag-{tags[index]}"+"{border-left: 10px solid var(--tag-background-" + str(index % len(css_backgrounds)) + ")!important;}")


# Function to create files for each row
def create_data_files(data):

    # Remove existing files
    shutil.rmtree(output_dir, ignore_errors=True)

    # Create the output dir if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for row in data['items']:
        values = row['values']

        # Get data from the colums
        title       = values[column_ids['title']]
        date        = values[column_ids['date']]
        tags        = values[column_ids['tags']]
        description = values[column_ids['description']]
        link        = values[column_ids['link']]
        image       = values[column_ids['image']]

        # Create a dictionary with the parsed data
        parsed_data = {
            'title'       : title,
            'date'        : date[0:10],
            'tags'        : [tag.strip() for tag in tags.split(',')],
            'description' : description,
            'link'        : link,
            'image'       : image
        }

        # Create a file with the parsed data
        file_name = f"{title.replace(' ', '_').lower()}.md"
        with open(f"{output_dir}/{file_name}", 'w') as file:
            file.write("+++\n")
            for key, value in parsed_data.items():
                if key == 'tags':
                    file.write(f'{key} = {json.dumps(value, indent=4)}\n')
                else:
                    file.write(f"{key} = \"{value}\"\n")
            file.write("+++\n")
            print(f"file added: {file_name}")


# Start the generation !
if __name__ == "__main__":
    coda_data = fetch_data_from_coda()
    if coda_data:
        extract_tags(coda_data)
        create_data_files(coda_data)
