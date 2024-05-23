import request_client
import lmdb

class CrawlPlanDatabaseClient:
    '''
    
    The crawl plans will be stored in databases, containing all of the urls that need to be crawled. This object is intended to manage a connection to the crawl database. 
    
    Parameters: 
        db_path : the path to the database file where the database exists

    '''

    def __init__(self, db_path: str):

        self.db_path = db_path 
        self.env = lmdb.open(self.db_path, create=True)
    
    def write_session(self):
        self.txn = self.env.begin(write=True)
        return self
    
    def read_session(self):
        self.txt = self.env.begin()
        return self
    
    @staticmethod
    def idx_bytes(idx: int) -> bytes:
        '''
        Given an index to a URL, return bytes representing the index
        '''
        return bytes(str(idx).encode())
    
    def read_url(self, url_idx: int):
        '''
        Given the index of a URL, read the URL from the database
        '''
        # convert the index to bytes
        url_idx_bytes = self.idx_bytes(url_idx)
        return self.txn.get(url_idx_bytes)

    def write_url(self, url: str, url_idx: int):
        '''
        Inserts a url into the crawl plan

        Parameters: 
            url: the url being inserted into the crawl plan 
            url_idx: the index of the url 
        '''
        # convert the index to bytes
        url_idx_bytes = self.idx_bytes(url_idx)

        # write the url into the database
        self.txn.put(url_idx_bytes, url)
    
    






if __name__ == "__main__": 

    crawl_plan_client = CrawlPlanDatabaseClient('').write_session()

