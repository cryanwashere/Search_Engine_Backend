'''

    This script crawls a subset of the wikipedia articles from the wikipedia title list

'''
import os
import requests
import parse
import concurrent.futures
import json
import sys
import index_data_structure


class Logger: 
    def __init__(self):
        pass
    def debug(self, message):
        if self.debug: 
            print(f"[debug] {message}")
    @staticmethod
    def format_number(num):
        num_str = str(num)
        return ' ' * (4 - len(num_str)) + num_str

logger = Logger()

# open the page list for wikipedia articles

# function for parsing the titles file
def title_from_line(line):
    return line[1:].replace(" ","").replace("\n","").replace("\t","")


class WikipediaCrawler:
    '''
    
        Crawler instance extists to crawl a certain subset of the wikipedia titles. Crawls all of the titles between 'crawl_start', and 'crawl_end'
    
    '''
    def __init__(self, crawl_size):
        
        # CREATE THE CRAWL SESSION WHICH WILL STORE THE DATA
        self.crawl_session = index_data_structure.CrawlSession()

        # IMPORTANT INFORMATION FOR THE CRAWL
        self.index_dir = "/home/sshfs_volume/index/page_index/"
        self.crawl_start = self.determine_next_crawl_start()
        self.crawl_end = self.crawl_start + crawl_size
        self.pages_to_crawl = crawl_size
        self.pages_crawled = 0
        self.titles_path = "/home/sshfs_volume/wikipedia/enwiki-titles"
        self.save_path = f"/home/sshfs_volume/index/page_index/wikipedia_{self.crawl_start}-{self.crawl_end}.json"



        # GET THE LIST OF TITLES THAT NEED TO BE CRAWLED
        self.titles = list()
        print("opening titles file")
        # open the title file, and grab a subset of the titles without opening the entire file (there would not be enough RAM to open up the entire file)
        with open(self.titles_path) as f:
            for i, line in enumerate(f):
                # make sure that we are just grabbing titles from the range of titles to be crawled in the current run 
                if i < self.crawl_start:
                    continue
                if i > self.crawl_end:
                    print("finished reading title file")
                    break
                # parse and store the title 
                title = title_from_line(line)
                self.titles.append(title)
            f.close()
        print(f"loaded {len(self.titles)} titles for crawling")
        

    def determine_next_crawl_start(self):
        # look through the files in the index, and determine where to resume the crawling process

        index_files = os.listdir(self.index_dir)
        
        # filter the files to only contain wikipedia index files
        index_files = [file for file in index_files if "wikipedia" in file]

        # get the strings detailing what section of the titles are contained in the files from each of the titles
        crawl_strings = [file.split('_')[-1].split('.')[0] for file in index_files]

        #print(crawl_strings)
        max_crawl_end = 0
        for string in crawl_strings:
            crawl_start, crawl_end = int(string.split('-')[0]), int(string.split('-')[1])

            if crawl_end > max_crawl_end:
                max_crawl_end = crawl_end
        
        return max_crawl_end + 1


    def process_title(self, title):
        '''
        
            This function is run on many threads. It will request the wikipedia page for each title, extract its data for the page index, upsert the data to the crawl session, and then print out the important information for the page
        
        '''

        # REQUEST THE WIKIPEDIA PAGE
        # make our url from the title 
        url = "https://en.wikipedia.org/wiki/" + title
        # wikipedia treats me better
        headers = {'User-Agent': 'BaleneSearchCrawler/0.0 (http://138.68.149.96:8000/search; cjryanwashere@gmail.com'}
        # get the html for the web page

        response = requests.get(url, headers=headers)
        if response.status_code == 200:



            # EXTRACT CONTENT FOR THE PAGE INDEX
            html_content = response.text  
            page = parse.extract_html(html_content, url)
            self.crawl_session.upsert(page)
                

            # PRINT OUT IMPORTANT INFORMATION ABOUT THE PAGE
            self.pages_crawled = self.pages_crawled + 1
            print(f"({self.pages_crawled} / {self.pages_to_crawl}) text sections: {Logger.format_number(len(page.text_sections))}, image urls: {Logger.format_number(len(page.image_urls))} page: {title}, ") 
            

        else:
            print(f"recieved non 200 status code (code {response.status_code}): {url}")
    
    def linear_crawler_process(self):

        print(f"crawling subset of wikipedia titles: {self.crawl_start} -> {self.crawl_end}")
        for title in self.titles:
            self.process_title(title)

        self.crawl_session.save(self.save_path)

    def async_crawler_process(self):

        '''
        
        Use a thread pool to asynchronously iniatiate the crawling process for each of the titles in the selected section
    
        '''

        print(f"crawling subset of wikipedia titles: {self.crawl_start} -> {self.crawl_end}")

        # concurrently download each page in the web site
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.process_title, self.titles)


        self.crawl_session.save(self.save_path)
        


if __name__ == "__main__" :

    wiki_crawler = WikipediaCrawler(500)
    wiki_crawler.linear_crawler_process()