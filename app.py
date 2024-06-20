import time
import numpy as np
from PIL import Image
import io
import json
import requests
from fastapi import FastAPI, File, UploadFile, Response
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sys


sys.path.append("./search_engine")
import search



search_client = search.SearchEngineClient(
    vector_index_path = "/home/cameron/Search_Engine/index_v1/vector_index",
    page_index_path = "/home/cameron/Search_Engine/index_v1/page_index"
)

app = FastAPI()



# host the browser search page
def search_page():
    with open("/home/cameron/Search_Engine/Search_Engine_Backend/search_page.html","r") as f:
        html =  f.read()
        return html
@app.get("/",response_class=HTMLResponse)
async def main_page():
    return search_page()


# search a text query
class TextSearchRequest(BaseModel):
    query: str
@app.post("/search_text")
async def search_text(text_search_request: TextSearchRequest):
    query = text_search_request.query
    results = search_client.search_text(query)
    print(results)
    results = [r.dict() for r in results]
    return JSONResponse({
        "search_result" : results
    })


# search an image 
@app.post("/search_image")
async def search_image(file: UploadFile = File(...)):
    # read the image data from the HTTP request and open it
    image = await file.read()
    pil_image = Image.open(io.BytesIO(image))
    results = search_client.search_image(pil_image)
    results = [r.dict() for r in results]
    return JSONResponse({
        "search_result" : results
    })
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
