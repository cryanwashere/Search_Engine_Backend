import os
import request_client
import page_index
import crawl_plan
import custom_logger
import time
import yaml


import multiprocessing
from multiprocessing import Process



class CrawlSession: 
    '''

        This object will orchestrate a single crawling process. It is meant to be run in a container, where it will will be initialized, and run. All of the parameters for a crawl session are meant to come from environment variables

    '''
    def __init__(self, crawl_plan_db_path: str, crawl_instruction: str, page_index_path: str, politeness: bool=False, multithreaded: bool=False):

        # whether or not to be polite to the hosts
        self.politeness = politeness

        # manage HTTP requests
        self.request_client = request_client.RequestClient()

        # manage the crawl_plan
        self.crawl_plan_client = crawl_plan.CrawlPlanDatabaseClient(crawl_plan_db_path)

        # manage the page index
        self.page_index_client = page_index.PageIndexClient(page_index_path)


        self.crawl_instruction = crawl_instruction
        self.start, self.end = self.parse_crawl_instruction(crawl_instruction)


        # logging
        self.logger = custom_logger.Logger("CrawlSession")
        self.logger.verbose = True
    
        if multithreaded:
            # lets try to do this with multiprocessing

            self.manager = multiprocessing.Manager()
        
            # queues for saving content that has been retrieved 
            self.asset_upsert_queue = self.manager.Queue(maxsize=2000)
            self.page_data_upsert_queue = self.manager.Queue(maxsize=2000)

            # queues for data to be retrieved
            self.page_url_queue = self.manager.Queue(maxsize=2000)
            self.asset_url_queue = self.manager.Queue(maxsize=2000)

        

    def parse_crawl_instruction(self, crawl_instruction):
        crawl_instruction = crawl_instruction.split('-')
        start, end = crawl_instruction[0], crawl_instruction[1]
        start, end = int(start), int(end)
        return start, end
    

    def upsert_image_bytes_async(self):
        # get the image  data from the asset upsert queue
        image_url, image_bytes = self.asset_upsert_queue.get()
        
        # upsert the bytes for the image
        self.page_index_client.upsert_image_bytes( image_url , image_bytes )
    
    def retieve_image_bytes_async(self):
        # get the next image in the asset url queue
        image_url = self.asset_url_queue.get()
        
        image_bytes = self.request_client.load_image_bytes(image_url)

        if image_bytes != None:
            # save the image data to the page index
            self.asset_upsert_queue.put(( image_url , image_bytes ))


    def upsert_page_data_async(self):
        # get the next page data in the queue
        page_data = self.page_data_queue.get()

        # upsert the page data to the index database
        self.page_index_client.upsert_page_data(page_data)


    def retrieve_page_data_async(self):
        # get the url of the next page to load from the queue
        page_url = self.page_url_queue.get()

        # retrieve the parse result, and parse its content
        parse_result = self.request_client.load_page_parse_result(page_url)
        
        if parse_result == None:
            return
        
        page_data = page_index.PageIndexData(**parse_result.page_dict)
        
        # put the page data into the upsert queue
        self.page_data_upsert_queue.put(page_data)

        # for each of the image urls in the page, put them into the asset url queue
        for image_url in page_data.image_urls: 
            self.asset_url_queue.put(image_url)

    def retrieve_page_data_process(self):
        # retrieve page data until the page url queue is finished
        while not (self.page_url_queue.is_empty()):
            self.retrieve_page_data_async()
    
    def retrieve_asset_process(self):
        while not (self.asset_url_queue.is_empty()):
            self.retrieve_image_bytes_async()

    def page_url_loader_process(self):
        # continuously load urls into the page url queue
        for i in range(self.start, self.end):

            # it will also be nescessary to implement a mechanism that will cause this process to sleep if the queue is too full
            while (self.page_url_queue.qsize() > 1000):
                time.sleep(1)

            page_url = self.crawl_plan_client.read_url(i)
            self.page_url_queue.put(page_url)



    def process_page(self, page_url: str):
        '''
        Given a URL for a page, upsert the page data for the URL, and its corresponding assets to the page index
        '''
        
        # request and extract the page content
        self.logger.log(f"getting page data for {page_url[-100:]}")

     
        request_start = time.time()

        # load the data for the page
        parse_result = self.request_client.load_page_parse_result(page_url)

        # the data for the page could not be loaded
        if parse_result == None:
            return
        
        request_end = time.time()


        page_data = page_index.PageIndexData(**parse_result.page_dict)

        # add the page data to the index
        self.page_index_client.upsert_page_data(page_data)

        upsert_end = time.time()

        # iterate through each of the images, and upsert each of them into the page index
        for image_url in page_data.image_urls:
            
            # request the bytes for the image 
            self.logger.log(f"\t getting image bytes for {image_url[-50:]}")
            image_bytes = self.request_client.load_image_bytes(image_url)

            if image_bytes != None: 
                # save the image data to the page index
                self.page_index_client.upsert_image_bytes( image_url , image_bytes )
        
        self.logger.log(f"request time: {request_end-request_start}s, upsert time: {upsert_end-request_end}s ")
        self.logger.log(f"page has {len(page_data.text_sections)} text sections and {len(page_data.image_urls)} image(s)")

    
    def crawl(self):

        start_time = time.time()

        for i in range(self.start, self.end):
            if self.politeness:
                time.sleep(2)
            self.logger.log(f"Crawling url {i}")
            #print(f"{i}/{self.end}")
            url = self.crawl_plan_client.read_url(i)
            self.process_page(url)

        end_time = time.time()
        total_time = end_time - start_time
        print(f"finished crawling. crawl took {total_time} seconds, averaging {total_time / (self.end-self.start)} seconds per page")
        
        # now that crawling has been finished, put an entry in the management file, indicating that the given section has been completed
        log_crawl_session("/project-dir/se-management/wikipedia_v1-sections.yml",self.crawl_instruction)

def log_crawl_session(se_management_path, crawl_instruction):
    with open(se_management_path,'r') as f:
        se_management = yaml.safe_load(f)
    

    se_management['Crawled Sections'].append(crawl_instruction)

    print(f"{se_management}")

    with open(se_management_path,'w') as f:
        yaml.dump(se_management, f)


if __name__ == "__main__":
    '''
    
        This section of the script will be where crawling sessions get initiated from inside their crawling containers. The parameters of the crawl will come from environment variables, which can be set specificially inside of the containers. The nescessary environment variables are: 

            CRAWL_PLAN_DB_PATH: the path to the database for the crawl plan

            CRAWL_INSTRUCTION: a string of the format: "(crawl start)-(crawl end)" 

            PAGE_INDEX_PATH: the path to the page index where the crawled data is stored

            POLITENESS: whether or not to be polite to the hosts

    '''

    # the path to the crawl plan database
    crawl_plan_db_path = os.environ['CRAWL_PLAN_DB_PATH']

    # a string representing what keys to crawl in the crawl session
    crawl_instruction = os.environ['CRAWL_INSTRUCTION']

    # path to the page index
    page_index_path = os.environ['PAGE_INDEX_PATH']

    politeness_str = os.environ['POLITENESS']
    if politeness_str == 'True':
        politeness = True
    else:
        politeness = False

    print(f"INITIALIZING CRAWL SESSION:\n CRAWL_PLAN_DB_PATH: {crawl_plan_db_path}\n CRAWL_INSTRUCTION: {crawl_instruction}\n PAGE_INDEX_PATH: {page_index_path}\n POLITENESS: {politeness}")

    crawl_session = CrawlSession(crawl_plan_db_path, crawl_instruction, page_index_path, politeness=politeness)

    crawl_session.crawl()
