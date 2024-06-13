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
import search





search_client = search.SearchEngineClient(
    vector_index_path = "~/Search_Engine/index_v1/vector_index",
    page_index_path = "~/Search_Engine/index_v1/page_index"
)

app = FastAPI()

app.mount("/static", StaticFiles(directory="/home/volume/Search_Engine_Backend/static"), name="static")

# host the browser search page
def search_page():
    with open("~/Search_Engine/Search_Engine_Backend/search_page.html","r") as f:
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
    return "hello"


# search an image 
@app.post("/search_image")
async def search_image(file: UploadFile = File(...)):
    # read the image data from the HTTP request and open it
    image = await file.read()
    pil_image = Image.open(io.BytesIO(image))
    results = search_client.search_image(pil_image)
    return "hello"
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
