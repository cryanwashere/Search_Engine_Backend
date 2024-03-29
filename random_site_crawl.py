import multiprocessing
from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, wait
from urllib.parse import urljoin, urlparse
import requests
import crawler.parse as parse
import json
import os
import sys
import re
import tldextract



image_set = set()
image_queue = list()

seed_url = sys.argv[1]


class RandomSiteCrawler:
    def __init__(self):
        self.pool = ThreadPoolExecutor(max_workers=5)

        self.scraped_pages = set([])
        self.finished_pages = set() # pages where the scrape process has been finished
        self.crawl_queue = Queue()
        self.crawl_queue.put(seed_url)

        self.max_urls = 2000

        self.futures = list()
    
    @staticmethod
    def filter_link(link):

        if "#" in link:
            return False

        if "%" in link:
            return False

        if "&" in link:
            return False

        return True

    @staticmethod
    def get_parent_domain(url):
        """
        Extracts the parent domain from a URL using regular expressions.

        Args:
            url: The URL string.

        Returns:
            The parent domain name, or None if the URL is invalid.
        """
        extracted = tldextract.extract(url)

        return 'https://{}.{}.{}'.format(extracted.subdomain, extracted.domain, extracted.suffix)

    def parse_links(self, html, parent_domain):

        links = list()
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
  

        # get only the links with hrefs
        links = [link for link in links if "href" in link.attrs]

        # get the references from the links
        links = [link["href"] for link in links]

        

        # clear out empy links
        links = [link for link in links if link != '']

        links = filter(self.filter_link, links)
        links = list(links)


        for i in range(len(links)):
            if not "https://" in links[i]:
                links[i] = urljoin(parent_domain,links[i])

        #print(links)

       
        return links

    def scrape_process(self, url):

        # request the html content of the url 
        response = requests.get(url)
        if response.status_code == 200:

            # get the html content from the web page
            html_content = response.text

            # this should work generally
            image_urls, text_sections = parse.extract_general_html(html_content, url)
            parent_domain = self.get_parent_domain(url)
            #print(f"parent domain: {parent_domain}")
            links = self.parse_links(html_content, parent_domain)
     

            print(f"[scrape_process] url: \033[1m{url[:100]}\033[0m, links: {len(links)} images: {len(image_urls)} queue size: {self.crawl_queue.qsize()}, crawled urls total: {len(self.scraped_pages)}  images total: {len(image_queue)} finished pages: {len(self.finished_pages)}")


            # iterate through the image urls and add them to the image queue
            for image_url in image_urls:
                if not image_url in image_set:
                    image_set.add(image_url)
            
                    image_upsert_request = {
                    "image_url" : image_url,
                    "page_url" : url
                    }

                    image_queue.append(image_upsert_request)

            # no need to grow the queue if the max page count has been reached
            if len(self.scraped_pages) >= self.max_urls:
                self.finished_pages.add(url)
                return 
            else:

                for link in links:
                    if not link in self.scraped_pages:
                        self.crawl_queue.put(link)
                
                self.finished_pages.add(url)

        else:
            print(f"[scrape process] failed to open page: {url}")

            
            
    
    def crawler_process(self):
        while True: 
            


            # stop crawling if we have reached the maximum url amount
            if len(self.scraped_pages) >= self.max_urls:
                print(f"reached url max, finishing process")
                break

            try:
                #print(f"{multiprocessing.current_process().name}: ")
                # the url currently being scraped
                target_url = self.crawl_queue.get(timeout=60)
                
                # make sure that the target url has not already been scraped
                if not target_url in self.scraped_pages:
                    print(f"[crawler_process] crawling: {target_url}")

                    self.scraped_pages.add(target_url)

                    # process the web page in another thread
                    job = self.pool.submit(self.scrape_process, target_url)
                    self.futures.append(job)

            except Empty:
                print("crawl queue is empty, finishing process...")
                return
            except Exception as e:
                print("error")
                print(e)
                continue
        wait(self.futures)

crawler = RandomSiteCrawler()
print(f"starting with: {seed_url}")
crawler.crawler_process()


save_path = os.path.join('/home/volume/index/image_queue/random_crawl', sys.argv[2] + '.json')
print(f"completed crawling with {len(image_queue)} image urls")
with open(save_path,'w') as f:
    json.dump(image_queue, f)
print(f"image queue saved to {save_path}")