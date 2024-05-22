import request_client
import sqlite3

class CrawlPlanDatabaseClient:
    '''
    
    The crawl plans will be stored in databases, containing all of the urls that need to be crawled. This object is intended to manage a connection to the crawl databsae
    
    Parameters: 
        db_path : the path to the database file where the database is stored

    '''

    def __init__(self, db_path: str):

        # connect to the database
        self.conn = sqlite3.connect(db_path)
        c = conn.cursor()



