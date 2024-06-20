from bs4 import BeautifulSoup
#import pywikibot
import requests
import parse
from custom_logger import Logger






class RequestClient: 

    '''    
    All HTTP requests made in this project should be done from inside a request client. The request client exists to manage complexity issues, such as specific headers for a crawl.
    '''
 
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
    
    def load_page_parse_result(self, page_url: str) -> dict:
        '''
        Given a url for a web page, load the html content of the url, and extract the data from the html content
        '''
        response = requests.get(page_url, headers=self.headers)

        if response.status_code == 200:
            # EXTRACT CONTENT FOR THE PAGE INDEX
            html_content = response.text  
            return parse.extract_html(html_content, page_url)

        else:
            self.logger.error(f"recieved non 200 status code (code {response.status_code}): {page_url}")
            return None
    
    def number_of_wiki_backlinks(self, page_url: str):
        '''
        given a URL to a wikipedia page, determine the number of backlinks that the page has
        '''
        # Replace 'your_page_title' with the actual Wikipedia page title
        page_title = page_url.split("/")[-1]

        site = pywikibot.Site('en','wikipedia')
        page = pywikibot.Page(site, page_title)

        # Get backlinks without following redirects to avoid infinite loops
        backlinks = list(page.backlinks(follow_redirects=False))

        return len(backlinks)
    
    def check_redirect(self, url):
        parse_result = self.load_page_parse_result(url)
        return parse_result.redirected

    


if __name__ == "__main__":
    # test out the request client, and the page index here

    request_client = RequestClient()


    