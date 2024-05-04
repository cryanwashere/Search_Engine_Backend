'''

    The purpose of this script is to open the files in the page index, and deliver important information about the pages. 

'''



import sys
import os
import json

def format_number(num):
        num_str = str(num)
        return ' ' * (5 - len(num_str)) + num_str

def load_json_data(filename):
    """
    This function loads a JSON file containing a list of dictionaries 
    and returns the list of dictionaries.

    Args:
        filename: The path to the JSON file.

    Returns:
        A list of dictionaries loaded from the JSON file.
    """
    try:
        # Open the file in read mode
        with open(filename, 'r') as infile:
            # Load the JSON data from the file
            data = json.load(infile)
            return data
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file {filename}.")
    return None

image_total = 0
text_total = 0
pages_total = 0
file_size_total = 0
page_index_path = "/home/sshfs_volume/index/page_index"
for filename in os.listdir(page_index_path):

    file_path = os.path.join(page_index_path, filename)
    file_size = os.stat(file_path).st_size / (1024 * 1024)

    file_dict = load_json_data(file_path)

    image_count = 0 
    text_count = 0
    page_count = 0 


    for page in file_dict['indexed_pages']:

        image_count += len(page['page_index_data']['image_urls'])
        text_count += len(page['page_index_data']['text_sections'])
        page_count += 1 

    print(f"{format_number(image_count)} images, {format_number(text_count)} text sections, {format_number(page_count)} pages,  size: {file_size:.2f} M  :  {filename}")

    image_total += image_count
    text_total += text_count
    pages_total += page_count 
    file_size_total += file_size

    # just to be safe
    del file_dict

print(f"total images: {format_number(image_total)}, total text sections: {format_number(text_total)}, total pages: {format_number(pages_total)}, total size: {file_size_total:.2f} M")