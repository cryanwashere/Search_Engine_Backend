'''


    The purpose of this is to generate an index given a queue of image upsert requests. The queue should be a JSON file containing a list of image and page urls


'''




import pickle
import os
import io
import time
import json
import requests

import open_clip
import torch
from PIL import Image
import numpy as np


import python_vector_search as pvs




#import multiprocessing
#from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
import requests


import crawler.parse as parse




# load an image, given its url
def open_image_from_url(url):
    try:
        # special header to inform wikipedia that we are a bot 
        # if we do not give wikipedia this header, our requests will often get denied, and we have a risk of being blocked
        headers = {'User-Agent': 'BaleneSearchCrawler/0.0 (http://138.68.149.96:8000/search; cjryanwashere@gmail.com'}

        # Send a GET request to the URL and get the image content
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for errors in the HTTP response

        # Open the image using Pillow and BytesIO
        image = Image.open(io.BytesIO(response.content))
        return image
    
    except Exception as e:
        print(e)
        return None

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


def upsert_image( model, payload: pvs.VectorPayload, client: pvs.VectorSearchClient ):

    '''
    
        Take in an image url, load the image, generate embeddings for it with CLIP, and then upsert the embeddings to the vector search client
    
    '''

    # make sure that it has not already been indexed
    # note that by using "image_url in client.hash_map" instead of "image_url in client.hash_map.keys()", we can check whether the image is in index in O(1) time instead of O(n) time.

    if payload.image_url in client.hash_map:
        return "already indexed"

    try:
        # fetch the image with an HTTP request
        image = open_image_from_url(payload.image_url)
    

        # if the request gives us the image
        if image is not None:

            # preprocess the image for the CLIP model
            image = preprocess(image).unsqueeze(0)

            # inference the model on the image
            with torch.no_grad():
                image_features = model.encode_image(image).squeeze()
                image_features = np.array(image_features)
    
    
            client.upsert(image_features, payload)

            return "success"
        return "failure"
    except Exception as e: 
        print(f"An error occurred in processing the image data: {e}")
        return "failure"

def upsert_text( model, text_section: str, payload: pvs.VectorPayload, client: pvs.VectorSearchClient ):

    try:
        # inference the model on the image
        with torch.no_grad():
            text_features = model.encode_text(tokenizer([text_section])).squeeze()
            text_features = np.array(text_features)

        text_client.upsert(text_features, payload)

        return "success"
    
    except Exception as e:
        print(f"An error occurred in processing the image data: {e}")
        return "failure"




if __name__ == "__main__":

    # load the CLIP models to encode image or text features
    model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
    tokenizer = open_clip.get_tokenizer('ViT-B-32')
    print("loaded CLIP models and tokenizer")

    page_index_path = "/home/sshfs_volume/index/page_index"
    image_index_path = "/home/sshfs_volume/index/vector_index/image"
    text_index_path = "/home/sshfs_volume/index/vector_index/text"


    # The script is going to open the page index, and determine if any of the files are missing in the image vector index folder
    page_index_files = os.listdir(page_index_path)
    image_vector_files = os.listdir(image_index_path)
    text_vector_files = os.listdir(text_index_path)

    # a list of all the filenames
    image_index_filenames = [file.split(".")[0] for file in image_vector_files]
    text_index_filenames = [file.split(".")[0] for file in text_vector_files]



    for file in page_index_files: 
        filename = file.split(".")[0]

        if not filename in text_index_filenames: 
            print(f"Generating text vector index for {filename}")

            
            text_client_path = os.path.join(text_index_path, filename + ".pkl")
            # generate a vector search client representing a single client path
            text_client = pvs.VectorSearchClient().file_client(text_client_path)
            

            page_list = load_json_data(os.path.join(page_index_path, file))['indexed_pages']

            for i, page in enumerate(page_list):
                
                print(f"[TEXT] ({i+1}/{len(page_list)}) Indexing text from: {page['page_index_data']['page_url']}")

                # for now, we just index the first text section in the page
                if len(page['page_index_data']['text_sections']) > 0:
                    text_section = page['page_index_data']['text_sections'][0]
                    text_section_id = f"(section0)_{page['page_index_data']['page_url']}"

                    # inference the model on the image
                    with torch.no_grad():
                        text_features = model.encode_text(tokenizer([text_section])).squeeze()
                        text_features = np.array(text_features)

                    # upsert the text section vector 
                    payload = pvs.VectorPayload(
                        page_id = page['page_id'],
                        page_url = page['page_index_data']['page_url'],
                        image_url = '',
                        text_section_id = text_section_id
                    )

                    text_client.upsert(text_features, payload)
            
            print(f"saving client with {text_client.point_count()} text sections to {text_client_path}")
            text_client.save()
        else: 
            print(f"text index already generated for file: {filename}")
        




        if not filename in image_index_filenames:
            print(f"Generating image vector index for {filename}")

            client_path = os.path.join(image_index_path, filename + ".pkl")
            # generate a vector search client representing a single client path
            client = pvs.VectorSearchClient().file_client(client_path)

            

            page_list = load_json_data(os.path.join(page_index_path, file))['indexed_pages']

            for i, page in enumerate(page_list):
                
                print(f"[IMAGE] ({i+1}/{len(page_list)}) Indexing page with {len(page['page_index_data']['image_urls'])} images: {page['page_index_data']['page_url']}")
                for image_url in page['page_index_data']['image_urls']:

                    # upsert the image url
                    upsert_result = upsert_image(pvs.VectorPayload(
                        page_id = page['page_id'],
                        page_url = page['page_index_data']['page_url'],
                        image_url = image_url,
                        text_section_id = ''
                    ))
                    print(f"\t image url: {image_url[:50]}, status: {upsert_result} ")
            
            print(f"saving to client with {client.point_count} images to {client_path}")
            client.save()
        else:
            print(f"image index already generated for file: {filename}")
        
        




