import os
import request_client
import page_index
import crawl_plan

class CrawlSession: 
    '''

        This object will orchestrate a single crawling process. It is meant to be run in a container, where it will will be initialized, and run. All of the parameters for a crawl session are meant to come from environment variables

    '''
    def __init__(self, crawl_plan_db_path, crawl_instruction, page_index_path):

        # manage HTTP requests
        self.reqeust_client = request_client.RequestClient()

        # manage the crawl_plan
        self.crawl_plan_client = crawl_plant.CrawlPlanDatabaseClient(crawl_plan_db_path).read_session()

        # manage the page index
        self.page_index_client = page_index.PageIndexClient(page_index_path)


        self.start, self.end = self.parse_crawl_instruction(crawl_instruction)

    def parse_crawl_instruction(self, crawl_instruction):
        crawl_instruction = crawl_instruction.split('-')
        start, end = crawl_instruction[0], crawl_instruction[1]
        start, end = int(start), int(end)
        return start, end

    
    def crawl(self):
        for i in range(self.start, self.end):
            url = self.crawl_plan_client.read_url(i)
            self.request_client.proccess_page(self.page_index_client, url)


if __name__ == "__main__":
    '''
    
        This section of the script will be where crawling sessions get initiated from inside their crawling containers. The parameters of the crawl will come from environment variables, which can be set specificially inside of the containers. The nescessary environment variables are: 

            CRAWL_PLAN_DB_PATH: the path to the database for the crawl plan

            CRAWL_INSTRUCTION: a string of the format: "(crawl start)-(crawl end)" 

            PAGE_INDEX_PATH: the path to the page index where the crawled data is stored

    '''

    # the path to the crawl plan database
    crawl_plan_db_path = os.environ['CRAWL_PLAN_DB_PATH']

    # a string representing what keys to crawl in the crawl session
    crawl_instruction = os.environ['CRAWL_INSTRUCTION']

    # path to the page index
    page_index_path = os.environ['PAGE_INDEX_PATH']

    crawl_session = CrawlSession(crawl_plan_db_path, crawl_instruction, page_index_path)

    crawl_session.crawl()