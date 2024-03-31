'''

    This is a server to facilitate remotely controlling the web crawler. 

'''
import threading
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import sys
sys.path.append('/home/Search_Engine_Backend')
from wikipedia_crawl import WikipediaCrawler
from pydantic import BaseModel

app = FastAPI()

wikipedia_crawler = WikipediaCrawler()



class CrawlingTask(threading.Thread):
    def run(self,*args,**kwargs):
        print("CrawlingTask.run")
        wikipedia_crawler.crawler_process()
crawling_task = CrawlingTask()


class WikipediaCrawlRequest(BaseModel):
    crawl_start: int
    crawl_end: int 
# set the target (subset of wikiepdia urls to crawl) for the wikipedia crawler
@app.post("/crawl_wikipedia")
async def set_wikipedia_target(crawl_request: WikipediaCrawlRequest):
    
    if wikipedia_crawler.status == "idle":
        wikipedia_crawler.set_target(
            crawl_request.crawl_start,
            crawl_request.crawl_end
        )

        crawling_task.start()

        return "process initiated"

    else:
        return "crawler is currently busy"



    


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
