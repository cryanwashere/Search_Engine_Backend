
from dataclasses import dataclass
import dataclasses
from typing import List
import uuid


import tldextract
import hashlib
import string

import os
import json

volume_path = os.environ["VOLUME_PATH"]
page_index_path = os.environ["PAGE_INDEX_PATH"]


'''
 
DATA STRUCTURE FOR THE PAGE INDEX FILES


    Here is the procedure for storing data for each of the indexed pages:

    page_id : a hash of the page data for identifying it
    page_index_data : 
        page_url : the url of the web page
        text sections : a list of strings containing the text from the web page
        image_urls : a list of strings containing the images from the web page
        time_indexed : a string representation of the time that the web page was indexed
    
    the files will be stored in JSON format

'''

@dataclass
class PageIndexData:

    page_url      : str
    text_sections : List[str]
    image_urls    : List[str]
    time_indexed  : str

@dataclass
class PageData:

    page_id         : str
    page_index_data : dict # takes on the form 

    def __init__(self, page_index_data):

        # the id for a an indexed page will always be the hash of its url, and the time that it was indexed, concatenated
        #self.page_id = str(hash(page_index_data.page_url + page_index_data.time_indexed))

        self.page_id = str(uuid.uuid1())

        self.page_index_data = page_index_data
    
    # convert the object completely into a dictionary
    def dict(self):
        return dataclasses.asdict(self)


'''

    for each page, its data will be stored as: 
    
        page_index/h/a/s/h/o/f/u/r/l/page_id.json

    a new page_id is generated every time the page is crawled, so often the page's directory may have multiple page data files for various crawls

'''


 

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
    return hex_digest[:10]


def page_url_dir(page_url : str):
    '''
    Given a page URL, find the directory in the page index where the index files of that page is being stored 
    '''
    page_url_hash = hash_url(page_url)
    page_path = "/".join(page_url_hash)

    # the directory where the page data gets saved
    save_dir = os.path.join( page_index_path, "page_index", page_path )
    return save_dir

def save_page_data(page_data : PageData):

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


class PageIndex:
    '''
    
        A python object representing a page index 
    
    '''
    def __init__(self, path):
        self.path = path   