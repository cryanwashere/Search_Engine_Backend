from PIL import Image
from dataclasses import dataclass
import dataclasses
from typing import List, Tuple
import uuid
import tldextract
import hashlib
import string
import os
import json
 


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
        self.page_data_path = os.path.join(self.path, "page_data")
        if not os.path.isdir(self.page_data_path):
            print("making page data directory")
            os.mkdir(self.page_data_path)

        # the path where all of the images data is stored
        self.asset_path = os.path.join(self.path, "asset")
        if not os.path.isdir(self.asset_path):
            print("making asset directory")
            os.mkdir(self.asset_path)
    
    def page_url_path(self, page_url : str):
        '''
        Given a page url, return the path to where it is stored

        Parameters: 
            page_url : the url of the page
        
        example usage:
            Input: 
                https://en.wikipedia.org/wiki/Google_Search
            Output: 
                path/page_data/b/d/8/9/6/0/9/3/8/3/0/f/f/a/b/bd896093830ffab91a6e0a02d6612e2c73c9b82db93304cdc18dad387ec1dc9b.json
        '''

        # the hash of the page url
        page_id = hex_digest_hash(page_url)

        # the path to where it exists in the file tree. the path comprises of the first 15 characters of its ID
        tree_path = "/".join(page_id[:15])  



        # the directory where the page data gets stored
        page_data_directory = os.path.join(self.page_data_path, tree_path)

        return page_data_directory, os.path.join(page_data_directory, page_id + ".json")

    def image_url_path(self, image_url : str):
        '''
        Given an image url, return the path to where it is stored

        Parameters: 
            page_url : the url of the image
        
        example usage:
            Input: 
                https://en.wikipedia.org/wiki/File:Google_Homepage.png
            Output: 
                path/asset/1/8/6/e/0/c/a/9/d/f/a/9/3/c/e/186e0ca9dfa93ce27b60f97616d5fde91ebbd20310575743f114dd08c6fac0f8.png
        '''

        # the hash of the page url
        image_id = hex_digest_hash(image_url)

        # the path to where it exists in the file tree. the path comprises of the first 15 characters of its ID
        tree_path = "/".join(image_id[:15])

        # this is nescessary for saving the image
        image_extension = image_url.split(".")[-1]

        # the directory where the page is stored
        image_directory = os.path.join(self.asset_path, tree_path)

        return image_directory, os.path.join(image_directory,  image_id + f".{image_extension}")

    def upsert_page_data(self, page_data : PageIndexData):
        # the path to save the page data
        page_save_dir, page_save_path = self.page_url_path(page_data.page_url)

        # if the directory where the page data is stored does not exist, make it
        if not os.path.isdir(page_save_dir):
            os.makedirs(page_save_dir)

        # save the page data as a JSON file
        with open(page_save_path, "w") as f:
            json.dump(page_data.dict(), f)

    def upsert_image_bytes(self, image_url : str, image_bytes : bytes):
        '''
        Upsert the image to the page index

        Parameters: 
            image_url : the url of the image being upserted
            image_bytes : the bytes of the image
        '''
        # the path to save the image
        image_save_dir, image_save_path = self.image_url_path(image_url)

        # if the directory where the image data is stored does not exist, make it
        if not os.path.isdir(image_save_dir):
            os.makedirs(image_save_dir)

        # save the file in whatever its correct format is: 
        with open(image_save_path, "wb") as f:
            f.write(image_bytes)
    
    def retrieve_page_data(self, page_url) -> PageIndexData:
        '''
        Given a page url, retrieve the page data if it has been indexed
        '''
        _, page_save_path = self.page_url_path(page_url)

        try:
            with open(page_save_path, "r") as f:
                page_data_dict = json.load(f)
                
                # convert to a PageData object
                page_data = PageIndexData(**page_data_dict)
                
                return page_data
        except Exception as e: 
            print(f"failed to load page data for url {page_url}: {e}")
    
    def retrieve_image(self, image_url) -> Image:
        '''
        Given an image url, retrieve the image if it has been indexed
        '''
        _, image_save_path = self.image_url_path(image_url)

        try:
            return Image.open(image_save_path)
        except Exception as e: 
            print(f"failed loading image: {e}")
    
    def retrieve_page_images(self, page_url: str) -> Tuple[PageIndexData, List[type(Image)]]:
        '''
        Given a page url, retrieve the data for the page, and all of the images in the page 
        '''

        # get the page data
        page_data = self.retreive_page_data(page_url)

        # for each of the images in the page, load the image
        image_list = list()
        for image_url in page_data.image_urls:
            image_list.append(self.retrieve_image(image_url))
        
        return page_data, image_list





if __name__ == "__main__":
    page_index_client = PageIndexClient("/home/cameron/Search_Engine/index_v1/page_index")
    
    #rabbit_page_data = page_index_client.retrieve_page_data("https://en.wikipedia.org/wiki/Rabbit")

    #print(page_index_client.image_url_path(rabbit_page_data.image_urls[0]))

    import sys

    command = sys.argv[1]

    #match command: 
    #    case "find_path":
    #        print(f"path for {sys.argv[2]}:")
    #        print(page_index_client.page_url_path(sys.argv[2]))
    #    case "show_page":
    #        print(f"showing page data for: {sys.argv[2]}")
    #        print(page_index_client.retrieve_page_data(sys.argv[2]))
    #    case "text":
    #        print(f"showing text sections for: {sys.argv[2]}")
    #        page_data = page_index_client.retrieve_page_data(sys.argv[2])
    #        for text_section in page_data.text_sections:
    #            print(text_section)
    #            print()

    #print(page_index_client.retrieve_page_data('https://en.wikipedia.org/wiki/!!!'))