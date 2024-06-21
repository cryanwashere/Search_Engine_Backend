from PIL import Image
from dataclasses import dataclass
import dataclasses
from typing import List, Tuple
import uuid
import io
import hashlib
import string
import os
import json
from sqlitedict import SqliteDict


'''
 
DATA STRUCTURE FOR THE PAGE INDEX ENTRIES


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

    # convert the object completely into a dictionary
    def dict(self):
        return dataclasses.asdict(self)



def hex_digest_hash(string: str) -> str:
    """
    Hashes a string using SHA-256 and returns a hexadecimal digest
    """
     # Generate the SHA-256 hash of the string
    hash_object = hashlib.sha256(string.encode())
    
    # Convert the hash to hexadecimal string
    hex_digest = hash_object.hexdigest()

    return hex_digest


class PageIndexClient:
    '''
    
        A python object representing a page index. 
        
        
        The page index has the following structure: 

            path
            ├── asset
            └── page_data 
    
    '''
    def __init__(self, path):
        
        # the root directory of the page index
        self.path = path 
        if not os.path.isdir(self.path):
            print("no index found at the given directory, making new index")
            os.mkdir(self.path)

        # the path where all the page data is stored
        self.page_data_path = os.path.join(self.path, "page_data.sqlite")
        # create connection to the page database
        self.page_data_db = SqliteDict(self.page_data_path)

        # the path where all of the images data is stored
        self.asset_path = os.path.join(self.path, "asset.sqlite")
        # create connection to the assets database
        self.asset_db = SqliteDict(self.asset_path)
    
    def get_page_id(self, page_url : str):
        # the hash of the page url
        return hex_digest_hash(page_url)

    def get_image_id(self, image_url : str):
        # the hash of the page url
        return hex_digest_hash(image_url)

    def upsert_page_data(self, page_data : PageIndexData):

        page_id = self.get_page_id(page_data.page_url)

        page_data_dict = page_data.dict()

        self.page_data_db[page_id] = page_data_dict
        self.page_data_db.commit()
    
    def check_page_url(self, url: str) -> bool:
        '''
        Check if the page URL has been crawled. Returns True if the page has been crawled, and returns False if the page has not been crawled
        '''
        page_id = self.get_page_id(url)
        return self.page_data_db[page_id] != None
        
    def upsert_image_bytes(self, image_url : str, image_bytes : bytes):
      
        image_id = self.get_image_id(image_url)

        self.asset_db[image_id] = image_bytes
        self.asset_db.commit()
    
    def commit(self):
        print("committing to page data and asset databases")
        self.asset_db.commit()
        self.page_data_db.commit()
    
    def retrieve_page_data(self, page_url: str) -> PageIndexData:
        '''
        Given a page url, retrieve the page data if it has been indexed
        '''
        
        try:
            page_id = self.get_page_id(page_url)
            page_data_dict = self.page_data_db[page_id]
            page_data = PageIndexData(**page_data_dict)
            return page_data
        except Exception as e: 
            print(f"failed to load page data for url {page_url}: {e}")
    
    def retrieve_image(self, image_url) -> Image:
        '''
        Given an image url, retrieve the image if it has been indexed
        '''
        image_id = self.get_image_id(image_url)

        try:
            return Image.open(io.BytesIO(self.asset_db[image_id]))
        except Exception as e: 
            print(f"failed loading image: {e}")
    
    def retrieve_page_and_images(self, page_url: str) -> Tuple[PageIndexData, List[type(Image)]]:
        '''
        Given a page url, retrieve the data for the page, and all of the images in the page 
        '''

        # get the page data
        page_data = self.retrieve_page_data(page_url)

        # for each of the images in the page, load the image
        image_list = list()
        for image_url in page_data.image_urls:
            image_list.append(self.retrieve_image(image_url))
        
        return page_data, page_data.image_urls, image_list





if __name__ == "__main__":
    page_index_client = PageIndexClient("/home/cameron/Search_Engine/index_v1/page_index")
    
    #rabbit_page_data = page_index_client.retrieve_page_data("https://en.wikipedia.org/wiki/Rabbit")

    #print(page_index_client.image_url_path(rabbit_page_data.image_urls[0]))

    import sys

    command = sys.argv[1]
 
    if command == "find_id":
        print(f"path for {sys.argv[2]}:")
        print(page_index_client.get_page_id(sys.argv[2]))
    elif command == "show_page":
        print(f"showing page data for: {sys.argv[2]}")
        print(page_index_client.retrieve_page_data(sys.argv[2]))
    elif command == "text":
        print(f"showing text sections for: {sys.argv[2]}")
        page_data = page_index_client.retrieve_page_data(sys.argv[2])
        if page_data == None:
            exit()
        for text_section in page_data.text_sections:
            print(text_section)
            print()
    elif command == "images":
        page_data = page_index_client.retrieve_page_data(sys.argv[2])
        for image_url in page_data.image_urls:
            print(image_url)
    elif command == "page_and_images":
        print(page_index_client.retrieve_page_and_images(sys.argv[2]))

    #print(page_index_client.retrieve_page_data('https://en.wikipedia.org/wiki/!!!'))
