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
import index_storage

# the filename of the titles file that is being crawled from 
titles_file_env = os.environ["TITLES_FILE"]
# the path to the volume on whatever machine the crawler is being run 
volume_path_env = os.environ['VOLUME_PATH']

sys.path.append(os.path.join(volume_path_env, "Search_Engine_Backend/search_engine"))
import python_vector_search as pvs
import open_clip
import torch
from PIL import Image
import numpy as np
import indexer 

from dataclasses import dataclass
from typing import List

import custom_logger

# load the CLIP models to encode image or text features
model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
tokenizer = open_clip.get_tokenizer('ViT-B-32')
print("loaded CLIP models and tokenizer")



logger = custom_logger.Logger()


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
        index_path # path of the index

    ):

        self.crawl_start = crawl_start
        self.crawl_end = crawl_end
        self.titles_path = titles_path
        self.page_index_path = os.path.join(index_path, "page_index")

        # IMPORTANT INFORMATION FOR THE CRAWL
        self.pages_crawled = 0

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
            self.pages_crawled = self.pages_crawled + 1

            
            # EXTRACT CONTENT FOR THE PAGE INDEX
            html_content = response.text  
            page = parse.extract_html(html_content, url)

            # save the data of the page to disk
            page_save_path = index_storage.save_page_data( page )


            logger.log(f"Crawling page: {page.page_index_data.page_url}")
            logger.log(f"data saved to: {page_save_path}")

            

            # for right now, we will only index the first text section in the wikipedia article. Otherwise, the vector index will grow way too fast
            for i, text_section in enumerate(page.index_data.text_sections[:1]):
                upsert_status = indexer.upsert_text(
                    model,
                    text_section = text_section, 
                    payload = pvs.VectorPayload(
                        image_url = "",
                        page_url = page.page_index_data.page_url,
                        _id = f"i_{page.page_index_data.page_url}",
                    ),
                    client = text_client,
                )
                logger.log(f"\t indexed text section")
            for image_url in page.index_data.image_urls: 
                upsert_status = indexer.upsert_image(
                    model, 
                    payload = pvs.VectorPayload(
                        image_url = image_url,
                        page_url = page.page_index_data.page_url,
                        _id = image_url
                    ),
                    client = image_client
                )
                logger.log(f"\t indexed image url: {image_url[:100]}")
            

        else:
            logger.error(f"recieved non 200 status code (code {response.status_code}): {url}")
    
    def linear_crawler_process(self):
        '''
        
            Just do the crawl one title at a time. It may be slower, but it is better for testing, because errors are easier to track
        
        '''
        print(f"crawling subset of wikipedia titles: {self.crawl_start} -> {self.crawl_end}")
        for title in self.titles:
            self.process_title(title)


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
        

@dataclass
class CrawlPlan:
    relative_sections_to_crawl : List


if __name__ == "__main__" :

    '''
    
        The goal of this script is to be able to crawl every title in the given titles file. The wikipedia crawler will be created and run repeatedly, until the process is finished. This way, in the likely event that the process is interupted, it can simply be restarted. Furthermore, the result of the crawl will be broken up into many files 
    
    '''


     
        


    

    logger.log(f"using titles file: {titles_file_env}")

    # the directory of the page index
    page_index_path = os.path.join(volume_path_env, "index2/page_index")
    # the directory of the index
    index_path = os.path.join(volume_path_env, "index2")


    # create the vector clients for this section of the crawl
    image_client = pvs.VectorSearchClient2(os.path.join(index_path, "vector_index/image"))
    text_client  = pvs.VectorSearchClient2(os.path.join(index_path, "vector_index/text" ))


    # the path to the crawl plan file for the titles file. The crawl plan file details what sections have been crawled, and what sections need to be crawled
    crawl_plan_path = os.path.join(volume_path_env, "wikipedia/crawl_plans", titles_file_env.split(".")[0] + ".json")
    if os.path.isfile(crawl_plan_path):
        logger.log(f"crawl plan file found at: {crawl_plan_path}")
        with open(crawl_plan_path, "r") as f:
            crawl_plan_dict = json.load(f)
        crawl_plan = CrawlPlan(**crawl_plan_dict)

        logger.log(f"loaded crawl plan: {crawl_plan.__dict__}")
        

    else: 
        logger.log(f"no crawl plan file detected. creating new file at: {crawl_plan_path}")

        # at this point, we need to plan out the process of crawling the given wikipedia file

        # the start and end of the crawl 
        absolute_crawl_duration = titles_file_env.split(".")[0].replace("enwiki-titles",'').split("-")
        absolute_crawl_start = int(absolute_crawl_duration[0])
        absolute_crawl_end = int(absolute_crawl_duration[1])

        # the start and end of the crawl, relative ot the file 
        relative_crawl_start = 0
        relative_crawl_end = absolute_crawl_end - absolute_crawl_start

        # breaking the crawl into sections of 500 
        crawl_sections = split_durations([(relative_crawl_start, relative_crawl_end)])

        crawl_plan = CrawlPlan(relative_sections_to_crawl = crawl_sections)
        logger.log(f"crawl plan created: \n {crawl_plan.__dict__}")

        # save the crawl plan
        with open(crawl_plan_path, "w") as f:
            json.dump(crawl_plan.__dict__, f)


    # Let's start crawling!



    # we will crawl, until each of the sections have been crawled in the crawl plan
    while len(crawl_plan.relative_sections_to_crawl) > 0:

        duration = crawl_plan.relative_sections_to_crawl[0]


        logger.log(f"crawling absolute duration: {duration[0]} -> {duration[1]}")
        crawler = WikipediaCrawler(
            duration[0],
            duration[1],
            titles_file_env,
            index_path 
        )
        crawler.linear_crawler_process()

        # get rid of the section that has just been crawled, and save the crawl plan
        crawl_plan.relative_sections_to_crawl = crawl_plan.relative_sections_to_crawl[1:]
        with open(crawl_plan_path, "w") as f:
            json.dump(crawl_plan.__dict__, f)


        # IDK if this is nescessary, but just to be on the safe side
        del crawler
        


