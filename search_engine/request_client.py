from bs4 import BeautifulSoup
import pywikibot
import requests
import parse
from custom_logger import Logger
import page_index





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
    
    def load_page_dict(self, page_url: str) -> dict:
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
        response = requests.get(url)
        soup = BeautifulSoup(response._content)
        canonical = soup.find('link', {'rel': 'canonical'})
        return canonical['href'] != url

    def process_page(self, page_index_client: page_index.PageIndexClient, page_url: str, use_redirects=False):
        
        # request and extract the page content
        self.logger.log(f"getting page data for {page_url[-100:]}")

        # load the data for the page
        parse_result = self.load_page_dict(page_url)

        # the data for the page could not be loaded
        if parse_result == None:
            return False

        page_data = page_index.PageIndexData(**parse_result.page_dict)

        # add the page data to the index
        page_index_client.upsert_page_data(page_data)

        # iterate through each of the images, and upsert each of them into the page index
        for image_url in page_data.image_urls:
            
            # request the bytes for the image 
            self.logger.log(f"\t getting image bytes for {image_url[-100:]}")
            image_bytes = self.load_image_bytes(image_url)

            if image_bytes != None: 
                # save the image data to the page index
                page_index_client.upsert_image_bytes( image_url , image_bytes )


if __name__ == "__main__":
    # test out the request client, and the page index here

    request_client = RequestClient()


    