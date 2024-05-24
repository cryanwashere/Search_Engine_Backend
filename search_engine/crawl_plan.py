from sqlitedict import SqliteDict


class CrawlPlanDatabaseClient:
    '''
    
    The crawl plans will be stored in databases, containing all of the urls that need to be crawled. This object is intended to manage a connection to the crawl database. 
    
    Parameters: 
        db_path : the path to the database file where the database exists

    '''

    def __init__(self, db_path: str):
        self.db = SqliteDict(db_path)
    
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

    def read_url(self, idx: int):
        return self.db[str(idx)]
    
    def finish(self):
        self.db.close()

    
    

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


