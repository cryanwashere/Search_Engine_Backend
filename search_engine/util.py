import json



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