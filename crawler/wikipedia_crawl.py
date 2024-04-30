'''

    This script crawls a subset of the wikipedia articles from the wikipedia title list

'''

import requests
import parse
import concurrent.futures
import json
import sys
import index_data_structure

# open the page list for wikipedia articles

# function for parsing the titles file
def title_from_line(line):
    return line[1:].replace(" ","").replace("\n","").replace("\t","")


class WikipediaCrawler:
    '''
    
        Crawler instance extists to crawl a certain subset of the wikipedia titles
    
    '''
    def __init__(self, crawl_start, crawl_end):
        
        self.session_data = data_structure.CrawlSession

        # the number of pages crawled by the wikipedia crawler 
        self.pages_crawled = 0

        self.titles_path = "/home/sshfs_volume/wikipedia/enwiki-titles"
        self.save_path = f"/home/sshfs_volume/index/image_queue/wikipedia/wikipedia_{crawl_start}-{crawl_end}.json"


         # the subset of wikipedia titles that are going to be crawled by the current crawler instance
        self.crawl_start = crawl_start
        self.crawl_end = crawl_end

        self.pages_to_crawl = crawl_end - crawl_start
        # moniter the amount of pages that have been crawled in the current run 
        self.pages_crawled = 0

        self.titles = list()

       


        

        print("opening titles file")
        # open the title file, and grab a subset of the titles without opening the entire file (there would not be enough RAM to open up the entire file)
        with open(self.titles_path) as f:
            for i, line in enumerate(f):

                # make sure that we are just grabbing titles from the range of titles to be crawled in the current run 
                if i < crawl_start:
                    continue
                if i > crawl_end:
                    print("finished reading title file")
                    break

                # parse and store the title 
                title = title_from_line(line)
                self.titles.append(title)
        print(f"loaded {len(self.titles)} titles for crawling")



    def process_title(self, title):
        #print(f"processing title: {title}")

        # make our url from the title 
        url = "https://en.wikipedia.org/wiki/" + title

        # wikipedia treats me better
        headers = {'User-Agent': 'BaleneSearchCrawler/0.0 (http://138.68.149.96:8000/search; cjryanwashere@gmail.com'}

        # get the html for the web page
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            

            html_content = response.text  

            
            # this should work generally
            page_dict = parse.extract_html(html_content, url)
           

            self.session_data.add(page_dict, url)

        
            self.pages_crawled = self.pages_crawled + 1

            print(f"({self.pages_crawled} / {self.pages_to_crawl}) page: {title}, text sections: {len(page_dict['text_sections'])}, image urls: {len(page_dict['image_urls'])}") 
        else:
            print(f"failed to open page: {url}")
            #with open(f"/home/wikipedia/error_html/error_{title}.html",'w') as f:
            #    f.write(response.text)
            #print("wrote response html")

    def crawler_process(self):

        print(f"crawling subset of wikipedia titles: {self.crawl_start} -> {self.crawl_end}")

        # concurrently download each page in the web site
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.process_title, self.titles)


        print(f"completed crawling with {len(self.image_queue)} image urls")

        self.session_data.save(self.save_path)
        


if __name__ == "__main__" :
    crawl_start = 10000
    crawl_end   = 15000

    wiki_crawler = WikipediaCrawler()
    wiki_crawler.set_target(crawl_start, crawl_end)

    wiki_crawler.crawler_process()