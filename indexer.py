'''


    The purpose of this is to generate an index given a queue of image upsert requests. The queue should be a JSON file containing a list of image and page urls: 

    [
        {
            "image_url" : "..."
            "page_url" : "..."
        },
        {
            "image_url" : "..."
            "page_url" : "..."
        }
        ...
    ]


'''




import pickle
import os
import io
import time
import json
import open_clip
import torch
import requests
from PIL import Image
import numpy as np




#import multiprocessing
#from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
import requests


import crawler.parse as parse
import python_vector_search as pvs

# load the CLIP models to encode image or text features
model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
tokenizer = open_clip.get_tokenizer('ViT-B-32')
print("loaded CLIP models and tokenizer")


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


def upsert_image_url( image_url, page_url):

    '''
    
        Take in an image url, load the image, generate embeddings for it with CLIP, and then upsert the embeddings to the vector search client
    
    '''

    # make sure that it has not already been indexed
    # note that by using "image_url in client.hash_map" instead of "image_url in client.hash_map.keys()", we can check whether the image is in index in O(1) time instead of O(n) time.
    t_hashcheck_start = time.time()
    if image_url in client.hash_map:
        return "already indexed"
    t_hashcheck_end = time.time()

    # fetch the image with an HTTP request
    t_imfetch_start = time.time()
    image = open_image_from_url(image_url)
    t_imfetch_end = time.time()

    # if the request gives us the image
    if image is not None:

        # preprocess the image for the CLIP model
        image = preprocess(image).unsqueeze(0)

        # inference the model on the image
        with torch.no_grad():
            image_features = model.encode_image(image).squeeze()
            image_features = np.array(image_features)
  
        # upsert the vector and its payload to the search client
        payload = pvs.VectorPayload(image_url, page_url)    
        client.upsert(image_features, payload)

        return "success"
    return "failure"



crawl_dir = "/home/sshfs_volume/index/page_index/"
for file in os.listdir(crawl_dir):
    
    print(f"Indexing image queue file: {file}")

    queue_path = os.path.join(crawl_dir, file)
    client_file = file.split(".")[0] + ".pkl"
    client_path = os.path.join("/home/sshfs_volume/index/vector_index/image", client_file)

    # load the vector search client
    client = pvs.VectorSearchClient(client_path)   

    # load the image queue
    page_list = load_json_data(queue_path)['indexed_pages']
    print(f"processing queue of {len(page_list)} pages")

    # iterate through the image queue normally
    for i, image_dict in enumerate(page_list):
        upsert_result = upsert_image_url(image_dict['image_url'], image_dict['page_url'])
        print(f"({i+1}/{len(image_queue)}) image url: {image_dict['image_url'][:100]}, status: {upsert_result} ")

    # save the client's progress
    client.save()
    print(f"saved vector client to {client_path}")
    
print("completed indexing last queue file. process complete. ")



'''

# load the vector search client
client = pvs.VectorSearchClient(client_path)   

# load the image queue
image_queue = load_json_data(queue_path)
print(f"processing queue of {len(image_queue)} images")

# iterate through the image queue normally
for i, image_dict in enumerate(image_queue):
    upsert_result = upsert_image_url(image_dict['image_url'], image_dict['page_url'])
    print(f"({i+1}/{len(image_queue)}) image url: {image_dict['image_url'][:100]}, status: {upsert_result} ")

# save the client's progress
client.save()
print("finished saving vector index. process complete.")











'''











# ignore this for now

class BatchIndexer: 
    '''
    
        meant to speed up the process of inferencing images. This will store a tensor, where images are continuously concatenated together. When the batch has reached a specific dimensionality, it will then generate features for the entire batch
    
    '''
    def __init__(self):
        
        self.batch = None
        self.batch_size = 32

        self.payload_queue = list()

    def up(self, image_tensor, image_payload):
        
        print(f"image tensor shape: {image_tensor.shape}")
        if self.batch is None:
            self.batch = image_tensor
        else: 
            self.batch = torch.cat((self.batch, image_tensor), 0)
        
        # one the batch size has been reached, the embedding generation operation is performed
        if self.batch.shape >= self.batch_size:
            pass

    def done(self):
        '''The process is finished, so embed whatever is left of the batch'''
        pass

