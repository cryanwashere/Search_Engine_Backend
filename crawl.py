import pickle
import os
import io
import time
import open_clip
import torch
import requests
from PIL import Image
import numpy as np

import multiprocessing
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
import requests

import crawler.scrape_wiki as scrape_wiki
import crawler.parse_wiki as parse_wiki
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


class Crawler:

    def __init__(self, client_path, crawl_path):

        self.client_path = client_path
        self.crawl_path = crawl_path
        
        # Load or create the crawl history, which is a set of all the web pages that have been crawled 
        if crawl_path is None or not os.path.isfile(crawl_path):
            print("previous crawl is nonexistent, creating new crawl")
            self.crawled_urls = set([])
        else:
            with open(crawl_path, "rb") as f:
                self.crawled_urls = pickle.load(f)
            print(f"opened crawl history with {len(self.crawled_urls)} urls")

        # load the vector search client
        self.client = pvs.VectorSearchClient(client_path)
        

        self.pool = ThreadPoolExecutor(max_workers=5)

        # queue of pages waiting to be crawled
        self.crawl_queue = Queue()


        self.images_indexed = 0
        self.urls_crawled_from_session = 0
        self.scrape_processes_completed = 0


    def upsert_image_url(self, image_url, page_url):

        '''
        
            Take in an image url, load the image, generate embeddings for it with CLIP, and then upsert the embeddings to the vector search client
        
        '''

        # make sure that it has not already been indexed
        # note that by usig "image_url in client.hash_map" instead of "image_url in client.hash_map.keys()", we can check whether the image is in index in O(1) time instead of O(n) time.
        t_hashcheck_start = time.time()
        if image_url in self.client.hash_map:
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
                t_encode_start = time.time()
                image_features = model.encode_image(image).squeeze()
                image_features = np.array(image_features)
                t_encode_end = time.time()

            # upsert the vector and its payload to the search client
            payload = pvs.VectorPayload(image_url, page_url)    
            self.client.upsert(image_features, payload)

            return "success"
        return "failure"

    def save_progress(self):
        # save the search client
        self.client.save()

        # save the list of visited urls
        with open(self.crawl_path, 'wb') as f:
            pickle.dump(self.crawled_urls, f)
            f.close()

        print("")
        print("PROGRESS SAVED SUCCESSFULLY")
        print("")            
        
    
    def scrape_process(self, url):
        
        # request the html content of the url 
        response = requests.get(url)
        if response.status_code == 200:

            # get the html content from the web page
            html_content = response.text

            # MANAGE LINKS TO OTHER PAGES

            # get all the links to other pages
            links = scrape_wiki.search_HTML(html_content)

            # add all of the links that have not been searched to the queue
            for link in links: 
                if not link in self.crawled_urls: 
                    self.crawl_queue.put(link)

            #MANAGE WEB PAGE CONTENT
            
            # get the image links and the text sections from the html
            image_urls, text_sections = parse_wiki.extract_html(html_content, url)

            # for each of the image urls, upsert them to the vector search client
            print(f"[scrape_process]: {url}, links: {len(links)} image urls: {len(image_urls)}\n")
            for image_url in image_urls[:20]:
                upsert_result = self.upsert_image_url(image_url, url)
                self.images_indexed +=1
                print(f"\timage: \033[1m{image_url[60:120]}\033[0m, result: {upsert_result}\n")
            print(f"total images indexed: {self.images_indexed}")


        # record that the scrape process has finished
        self.scrape_processes_completed += 1
            
            

    
    def crawler_process(self):
        while True: 
            try:
                #print(f"{multiprocessing.current_process().name}: ")

                # slow down for the scrape process if nescessary
                if len(self.crawled_urls) - self.scrape_processes_completed > 100:
                    continue

                # the url currently being scraped
                target_url = self.crawl_queue.get(timeout=60)
                
                # make sure that the target url has not already been scraped
                if target_url not in self.crawled_urls:

                    self.crawled_urls.add(target_url)
                    self.urls_crawled_from_session += 1

                    print(f"[crawler_process] url: \033[1m{target_url[27:80]}\033[0m, queue size: {self.crawl_queue.qsize()}, crawled urls session: {self.urls_crawled_from_session} crawled urls total: {len(self.crawled_urls)} scrape processes: {self.scrape_processes_completed}")

                    # save the progress every 100 urls
                    if len(self.crawled_urls) % 100 == 0:
                        self.save_progress()

                    # process the web page in another thread
                    job = self.pool.submit(self.scrape_process, target_url)

            except Empty:
                print("crawl queue is empty, finishing process...")
                return
            except Exception as e:
                print("error")
                print(e)
                continue





# create the crawler
crawler = Crawler("/home/index/3.client", "/home/index/3.crawl2")


# the  urls to start depth first search from
# I chose them completely arbitrarily
seed_urls = [
    'https://en.wikipedia.org/wiki/Google_Search',
    'https://en.wikipedia.org/wiki/Butterfly',
    'https://en.wikipedia.org/wiki/Tower_of_London',
    'https://en.wikipedia.org/wiki/Vaseline',
    'https://en.wikipedia.org/wiki/Cloud',
]

crawler.crawl_queue.put(seed_urls[1])
crawler.crawler_process()