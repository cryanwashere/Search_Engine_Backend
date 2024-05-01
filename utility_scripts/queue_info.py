import os
import json

path = "/home/sshfs_volume/index/image_queue/random_crawl"


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


queue_files = os.listdir(path)

print(f"Gathering info for files stored at: {path}")

total_images = 0

for file_name in queue_files:

    if file_name.split(".")[-1] == "json":
        file_path = os.path.join(path, file_name)

        image_queue = load_json_data(file_path)

        print(f"{file_name}: {len(image_queue)} images")

        total_images += len(image_queue)

print(f"there are {total_images} images in total")
