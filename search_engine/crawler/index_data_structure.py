import json
import time
from dataclasses import dataclass
import dataclasses
from typing import List
import uuid

    
'''

DATA STRUCTURE FOR THE PAGE INDEX


    Here is the procedure for storing data for each of the indexed pages:

    page_id : a hash of the page data for identifying it
    page_index_data : 
        page_url : the url of the web page
        text sections : a list of strings containing the text from the web page
        image_urls : a list of strings containing the images from the web page
        time_indexed : a string representation of the time that the web page was indexed

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
@dataclass 
class CrawlSessionMetadata:

    time_started   : str
    images_indexed : bool
    pages_indexed  : bool



@dataclass
class CrawlSession: 

    metadata : CrawlSessionMetadata
    indexed_pages : List[PageData]

    def __init__(self):
        self.metadata = CrawlSessionMetadata(str(time.time()), False, False)
        self.indexed_pages = list()
    
    # add data to the crawl session 
    def upsert(self, page_index_data : PageIndexData):
        
        self.indexed_pages.append(
            PageData( page_index_data )
        )
    
    # convert to a dictionary
    def dict(self):
        return dataclasses.asdict(self)

    def save(self, save_path):
        print(f"saving to {save_path}")
        with open(save_path, "w") as f: 
            json.dump(self.dict(), f)




'''