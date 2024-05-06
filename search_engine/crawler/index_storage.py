'''

    An important challenge in this project is the storage of large amounts of files that can be quickly and easily indexed.


    page_index/h/a/s/h/o/f/u/r/l/page_id.json

'''
import index_data_structure as ids
import tldextract
import hashlib
import string

import os
import json

volume_path = os.environ["VOLUME_PATH"]
page_index_path = os.environ["PAGE_INDEX_PATH"]



#WRITTEN BY GEMINI
def hash_url(string : str):
    """
    Hashes a string using SHA-256 and returns a hexadecimal digest containing only numbers and letters.
    """
    # Generate the SHA-256 hash of the string
    hash_object = hashlib.sha256(string.encode())
    
    # Convert the hash to hexadecimal string
    hex_digest = hash_object.hexdigest()
    
    # there is no need for the hash to be giant
    return hex_digest[:5]


def page_url_dir(page_url : str):
    '''
    Given a page URL, find the directory in the page index where the index files of that page is being stored 
    '''
    page_url_hash = hash_url(page_url)
    page_path = "/".join(page_url_hash)

    # the directory where the page data gets saved
    save_dir = os.path.join( page_index_path, "page_index", page_path )
    return save_dir

def save_page_data(page_data : ids.PageData):

    page_url = page_data.page_index_data.page_url
    page_id = page_data.page_id

    save_dir = page_url_dir(page_url)

    # make the directory where the index file is stored
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)

    # the page data will be stored as a JSON file
    save_path = os.path.join(save_dir, page_id + ".json")
    
    # save the page data
    with open(save_path, "w") as f:
        json.dump(page_data.dict(), f)
    
    return save_path