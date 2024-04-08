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

import random_site_crawl as rsc

app = FastAPI()

'''
wikipedia_crawler = WikipediaCrawler()



class CrawlingTask(threading.Thread):
    def run(self,*args,**kwargs):
        print("CrawlingTask.run")
        wikipedia_crawler.crawler_process()
crawling_task = CrawlingTask()




@app.get("/logs")
async def logs():
    with open("/home/logs/server.out",'r') as f:
        return f.read()

class WikipediaCrawlRequest(BaseModel):
    crawl_start: int
    crawl_end: int 


# set the target (subset of wikiepdia urls to crawl) for the wikipedia crawler
@app.post("/crawl_wikipedia")
async def crawl_wikipedia(crawl_request: WikipediaCrawlRequest):
    return "service is not active"
    
    if wikipedia_crawler.status == "idle":
        wikipedia_crawler.set_target(
            crawl_request.crawl_start,
            crawl_request.crawl_end
        )

        crawling_task.start()

        return "process initiated"

    else:
        return "crawler is currently busy"

'''

seed_url = ""
save_file = "random-7"


class RandomCrawlingTask(threading.Thread):
    def run(self,*args,**kwargs):
        print(f"[RandomCrawlingTask.run] seed_url: {seed_url} save_path: {save_fileh}")
        rsc.crawl(seed_url, save_file)
random_crawling_task = RandomCrawlingTask()

class RandomCrawlRequest(BaseModel):
    seed_url: str


@app.post("/random_crawl")
async def random_crawl(crawl_request: RandomCrawlRequest):
    global seed_url
    seed_url = crawl_request.seed_url


    random_crawling_task.start()

    return "process initiated"

@app.get("/status")
async def status():
    

    


    


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
