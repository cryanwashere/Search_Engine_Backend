from sqlitedict import SqliteDict
import request_client
import parse

class CrawlPlanDatabaseClient:
    '''
    
    The crawl plans will be stored in databases, containing all of the urls that need to be crawled. This object is intended to manage a connection to the crawl database. 
    
    Parameters: 
        db_path : the path to the database file where the database exists

    '''

    def __init__(self, db_path: str):
        self.db = SqliteDict(db_path)
    
    def read_url(self, idx: int):
        return self.db[str(idx)]
    
    def finish(self):
        self.db.close()

    
    def load_wikipedia_titles(self, wikipedia_titles_path):
        '''
        Given the wikipedia title file, this will open the file, and load the URL for all of the titles into the database
        '''
        with open(wikipedia_titles_path) as f:
            for i, line in enumerate(f):
                if i == 0:
                    continue
                title = title_from_line(line)
                if i % 10000:
                    print(f"processing title {i}: {title}")
                url = url_from_title(title)
                self.db[i] = url
                self.db.commit()
            f.close()
            print("process finished")



    
    


    def filter_url_db(self, url_db_path):
        '''
        Given another url db path, open that crawl plan, and check all the urls. The urls that get filtered will be saved
        '''
        self.request_client = request_client.RequestClient()

        import threading
        import concurrent.futures

        self.db_to_filter = CrawlPlanDatabaseClient(url_db_path)
    

    def filter_url(self, url) -> bool:
        '''
        determine if the URL should be crawled
        '''

        is_redirect = self.request_client.check_redirect(url)
        return is_redirect
    
    def upsert_if_filtered(self, i):
        url = self.db_to_filter.read_url(i)
        if self.filter_url(url):
            self.db[]




        

    
    
    

def title_from_line(line):
    return line[1:].replace(" ","").replace("\n","").replace("\t","")
def url_from_title(title):
    return "https://en.wikipedia.org/wiki/" + title

if __name__ == "__main__": 

    crawl_plan_client = CrawlPlanDatabaseClient('/home/cameron/Search_Engine/wikipedia/wiki_title_db.sqlite')#.write_session()

    #crawl_plan_client.load_wikipedia_titles('/home/cameron/Search_Engine/wikipedia/enwiki_titles')
    
    for i in range(1,10):
        print(crawl_plan_client.read_url(i))

    crawl_plan_client.finish()


