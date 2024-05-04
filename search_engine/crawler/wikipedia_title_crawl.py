'''

    This script crawls a subset of the wikipedia articles from the wikipedia title list. It requires the following environment variables

        TITLES_FILE
        VOLUME_PATH

'''
import os
import requests
import parse
import concurrent.futures
import json
import sys
import index_data_structure

import uuid


class Logger: 
    def __init__(self):
        pass
    def debug(self, message):
        if self.debug: 
            print(f"[debug] {message}")
    def error(self, message):
        print(f"[ERROR] {message}")
    def log(self, message):
        print(f"{message}")
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
    def __init__(self, 
    
        crawl_start, # relative 
        crawl_end, # relative
        titles_path,
        index_path

    ):

        self.crawl_start = crawl_start
        self.crawl_end = crawl_end
        self.titles_path = titles_path
        self.index_path = index_path
        
       
        
        # CREATE THE CRAWL SESSION WHICH WILL STORE THE DATA
        self.crawl_session = index_data_structure.CrawlSession()

        # IMPORTANT INFORMATION FOR THE CRAWL
        self.pages_crawled = 0
        self.save_path = os.path.join( index_path, f"wikipedia_{self.crawl_start}-{self.crawl_end}.json" )


        print(f"crawling file-relative duration: {crawl_start} -> {crawl_end}")

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
            print(f"({self.pages_crawled + self.crawl_start} / {self.pages_to_crawl + self.crawl_start}) text sections: {Logger.format_number(len(page.text_sections))}, image urls: {Logger.format_number(len(page.image_urls))} page: {title}, ") 
            

        else:
            print(f"recieved non 200 status code (code {response.status_code}): {url}")
    
    def linear_crawler_process(self):
        '''
        
            Just do the crawl one title at a time. It may be slower, but it is better for testing, because errors are easier to track
        
        '''
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



def titles_file_duration(titles_file_path: str):
    '''
    
        Given a titles file path (which has the duration of the titles in it), return a tuple representing the titles contained in the titles file. Note that this is for title files which have already been split, not for the main titles file ('enwiki-titles')
    
    '''

    # get the name of the file
    file_name = titles_file_path.split("/")[-1]

    # replace irrelevant parts of the string
    duration_string = file_name.replace("enwiki-titles","").replace(".txt","")
    duration_list = duration_string.split("-")

    start, end = int(duration_list[0]), int(duration_list[1])

    return (start, end)

def crawl_durations(index_dir: str):
    '''
    
        The purpose of this method is to look into the page index directory, and gather information about what has already been crawled. 
    
    '''

    index_files = os.listdir(index_dir)
    
    # filter the files to only contain wikipedia index files
    index_files = [file for file in index_files if "wikipedia" in file]

    # get the strings detailing what section of the titles are contained in the files from each of the titles
    crawl_strings = [file.split('_')[-1].split('.')[0] for file in index_files]

    # a list of tuples, representing what durations have been crawled
    durations = list()

    max_crawl_end = 0
    for string in crawl_strings:
        crawl_start, crawl_end = int(string.split('-')[0]), int(string.split('-')[1])

        durations.append((crawl_start, crawl_end))

        if crawl_end > max_crawl_end:
            max_crawl_end = crawl_end
    
    return durations
    
    

def find_missing_durations(durations, absolute_start, absolute_end):
  """
  Finds all durations between absolute_start and absolute_end that are not in the list.

  Args:
    durations: A list of tuples representing durations.
    absolute_start: The starting absolute time.
    absolute_end: The ending absolute time.

  Returns:
    A list of tuples representing missing durations.
  """
  missing_durations = []
  current_time = absolute_start
  durations.sort()

  for start, end in durations:
    # Check if there's a gap between current_time and the start of the current duration
    if current_time < start:
      missing_durations.append((current_time, start))
    current_time = max(current_time, end)

  # Check if there's a gap between the end of the last duration and absolute_end
  if current_time < absolute_end:
    missing_durations.append((current_time, absolute_end))

  return missing_durations

def split_durations(durations, max_duration=500):
    """
    Splits durations larger than max_duration into chunks of size max_duration or less.

    Args:
        durations: A list of tuples representing durations.
        max_duration: The maximum allowed duration for a single chunk.

    Returns:
        A list of tuples representing split durations.
    """
    split_durations = []
    for start, end in durations:
        if end - start > max_duration:
            current_start = start
            while current_start < end:
                next_end = min(current_start + max_duration, end)
                split_durations.append((current_start, next_end))
                current_start = next_end
        else:
            split_durations.append((start, end))

    split_durations = list(filter(lambda x : x[1] - x[0] > 1 , split_durations))
    return split_durations
        



if __name__ == "__main__" :

    '''
    
        The goal of this script is to be able to crawl every title in the given titles file. The wikipedia crawler will be created and run repeatedly, until the process is finished. This way, in the likely event that the process is interupted, it can simply be restarted. Furthermore, the result of the crawl will be broken up into many files 
    
    '''


    titles_file_env = os.environ["TITLES_FILE"]
    volume_path_env = os.environ['VOLUME_PATH']

    logger.log(f"using titles file: {titles_file_env}")

    # the directory of the page index
    page_index_path = os.path.join(volume_path_env, "index/page_index")
    # the durations that have already been crawled. 
    indexed_duration_list = crawl_durations(page_index_path)

    
    # the absolute duration of titles to crawl
    crawl_duration = titles_file_duration(titles_file_env)
    absolute_start, absolute_end = crawl_duration

    # the script is meant to crawl every uncrawled section in between absolute_start, and absolute_end
    durations_to_crawl = split_durations(find_missing_durations(
        indexed_duration_list,
        absolute_start, 
        absolute_end
    ))
    
    print(f"crawling the following title durations: {durations_to_crawl}")

    for duration_start, duration_end in durations_to_crawl:
        print(f"crawling absolute duration: {duration_start} -> {duration_end}")
        crawler = WikipediaCrawler(
            duration_start - absoulte_start,
            duration_end - absolute_start,
            titles_file_env,
            page_index_path 
        )
        crawler.linear_crawler_process()


   
        


