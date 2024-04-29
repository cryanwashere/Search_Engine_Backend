import json
import time

def create_page_dict(
    page_url,
    text_sections,
    image_urls, 
):
'''

    Creates a dictionary for storing the data from the page in the index. The dictionary will have the following structure: 


    id : a hash of the page data for identifying it
    data : 
        page_url : the url of the web page
        text sections : a list of strings containing the text from the web page
        image_urls : a list of strings containing the images from the web page
        time_indexed : a string representation of the time that the web page was indexed


'''

    # put the data for the page into a python dictionary
    data = {
        "page_url" : page_url,
        "text_sections" : text_sections,
        "image_urls" : image_urls,
        "time_indexed" : time.strftime()
    }

    # the id of for the page is the has for its data
    page_id = hash(data)

    page_data = {
        "id" : page_id,
        "data" : data
    }

    return page_data

class Crawl_Session: 
    __init__(self):

        # a list of page dictionaries for all of the pages that have been crawled
        self.pages = list()
