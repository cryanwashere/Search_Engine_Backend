'''

    This is a server to facilitate remotely controlling the web crawler. 

'''

from threading import Thread
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from .wikipedia_crawl import WikipediaCrawler

app = FastAPI()

wikipedia_crawler = WikipediaCrawler()

# set the target (subset of wikiepdia urls to crawl) for the wikipedia crawler
@app.post("/set_wikipedia_target")
async def set_wikipedia_target(params: dict):
    wikipedia_crawler.set_target()


if __name__ == 'main':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
    print(f"Completed server process. {images_upserted} image features upserted to the index")