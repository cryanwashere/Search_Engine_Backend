'''

    The purpose of this file is to contain code for the RequestClient object. All HTTP requests made in this project should be done from inside a request client. The request client exists to manage complexity issues, such as specific headers for a crawl.

'''
 

import requests
import parse
from custom_logger import Logger
import page_index





class RequestClient: 
    def __init__(self):
        
        # for wikipedia.
        self.headers = {'User-Agent': 'BaleneSearchCrawler/0.0 (https://balene.wiki/search; cjryanwashere@gmail.com'}

        # for logging information about the crawl
        self.logger = Logger("RequestClient")

    def load_image_bytes(self, url : str) -> bytes:
        '''
        Given an image url, load the bytes of the image
        '''
        try:
            # Send a GET request to the URL and get the image content
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Check for errors in the HTTP response

            return response.content
        
        except Exception as e:
            self.logger.error(e)
            return None
    
    def load_page_dict(page_url: str) -> dict:
        '''
        Given a url for a web page, load the html content of the url, and extract the data from the html content
        '''
        response = requests.get(page_url, headers=self.headers)
        if response.status_code == 200:
            # EXTRACT CONTENT FOR THE PAGE INDEX
            html_content = response.text  
            page_dict = parse.extract_html(html_content, page_url)

            return page_dict

        else:
            self.logger.error(f"recieved non 200 status code (code {response.status_code}): {url}")


    def process_page(self, page_index_client: page_index.PageIndexClient, page_url: str):
        
        # request and extract the page content
        page_data = page_index.PageIndexData(**self.load_page_dict(page_url))

        # add the page data to the index
        page_index_client.upsert_page_data(page_data)

        # iterate through each of the images, and upsert each of them into the page index
        for image_url in page_data.image_urls:
            
            # request the bytes for the image 
            image_bytes = self.load_image_bytes(image_url)

            # save the image data to the page index
            page_index_client.upsert_image_bytes( image_url , image_bytes )


