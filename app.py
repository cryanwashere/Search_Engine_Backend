import open_clip
import time
import torch
import numpy as np
from PIL import Image
import io
import json
from torchvision import transforms
import torchvision
from torch import nn
import requests
from fastapi import FastAPI, File, UploadFile, Response
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import search_engine.python_vector_search as pvs
import sys
from pydantic import BaseModel
import ssl

#client_path = sys.argv[1]
client_path = "/home/volume/index/vector_index/image"
# load the vector search client
client = pvs.VectorSearchClient().directory_client(client_path)
# create a point matrix for the search client
client.create_point_matrix()
# keep track of how many images have been upserted since the server was started
images_upserted = 0



text_client_path = "/home/volume/index/vector_index/text"
text_client = pvs.VectorSearchClient().directory_client(text_client_path)
text_client.create_point_matrix()





# load the CLIP models
model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
tokenizer = open_clip.get_tokenizer('ViT-B-32')
print("loaded CLIP models and tokenizer")

# Special keys to determine if anything special should be done to an image being searched
with torch.no_grad():
    special_keys = ["plant", "mushroom", "animal", "insect"]
    special_key_vecs = model.encode_text(tokenizer(special_keys))




#app = FastAPI(ssl_keyfile="private.key", ssl_certfile="cert.crt")

app = FastAPI()

app.mount("/static", StaticFiles(directory="/home/volume/Search_Engine_Backend/static"), name="static")



# load an image, given its url
def open_image_from_url(url):
    try:
        # special header to inform wikipedia that we are a bot 
        # if we do not give wikipedia this header, our requests will often get denied, and we have a risk of being blocked
        headers = {'User-Agent': 'BaleneSearchCrawler/0.0 (http://209.97.152.154:8000/search; cjryanwashere@gmail.com'}

        # Send a GET request to the URL and get the image content
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for errors in the HTTP response

        # Open the image using Pillow and BytesIO
        image = Image.open(io.BytesIO(response.content))
        return image
    
    except Exception as e:
        return None

# host the browser search page
def search_page():
    with open("/home/volume/Search_Engine_Backend/search_page.html","r") as f:
        html =  f.read()
        html = html.replace("<!--INDEX_INFO-->",f"<p>{client.point_count()} images and {text_client.point_count()} text sections have been indexed</p>")

        return html

@app.get("/",response_class=HTMLResponse)
async def main_page():
    return search_page()
@app.get("/search",response_class=HTMLResponse)
async def search():
    return search_page()

@app.get("/ads.txt")
async def adds():
    return Response(content="google.com, pub-5375512399591036, DIRECT, f08c47fec0942fa0", media_type="text/plain")

# search a text query
class TextSearchRequest(BaseModel):
    query: str


def search_embedding(query_embedding):
    # search the image features with the search client

    text_results = text_client.search2(query_embedding)
    text_results = [r.payload.json() for r in text_results]

    results = client.search2(query_embedding)
    # convert the search results to a list of JSON strings
    results = [r.payload.json() for r in results]

    #return JSONResponse(content={"search_result": results, "nat_predictions": iNat_results})
    return JSONResponse(content={"search_result": results , "text_search_result" : text_results})

@app.post("/search_text")
async def search_text(text_search_request: TextSearchRequest):
    query = text_search_request.query

    with torch.no_grad():
        t_encode_start = time.time()
        query_embedding = model.encode_text(tokenizer([query]))
        t_encode_end = time.time()

        query_embedding = np.array(query_embedding).squeeze()

    return search_embedding(query_embedding)

# search an image 
@app.post("/search_image")
async def search_image(file: UploadFile = File(...)):
    # read the image data from the HTTP request and open it
    image = await file.read()
    pil_image = Image.open(io.BytesIO(image))

    # preprocess the Pillow image using the transform from open_clip
    image = preprocess(pil_image).unsqueeze(0)

    # inference the model on the image
    with torch.no_grad():

        # encode the image with the CLIP model
        t_encode_start = time.time()
        image_features = model.encode_image(image).squeeze()
        t_encode_end = time.time()

    
        t_natinf_start = time.time()
        '''
        # compare the image features with each of the special keys
        special_key_scores = image_features @ special_key_vecs.T

        # if we want to print out the scores for each of the key phrases
        for i, score in enumerate(special_key_scores):
            print(f"{special_keys[i]}: {score}")
        
        # If its score is high enough for one of the special keys, inference the iNaturalist model on the image
        if max(special_key_scores) > 20:
            iNat_results = iNat_inference(iNat_transform(pil_image.convert('RGB')).unsqueeze(0))
        else:
            iNat_results = []
        '''
        t_natinf_end = time.time()
        

        # convert the features to a NumPy array so that it can be searched
        image_features = np.array(image_features)
    
    # search the image features with the search client
    t_search_start = time.time()
    results = client.search2(image_features)
    t_search_end = time.time()

    # convert the search results to a list of JSON strings
    results = [r.payload.json() for r in results]

    print(f"image encoding time: {t_encode_end - t_encode_start}s, nat inf time: {t_natinf_end - t_natinf_start}s,  search time: {t_search_end - t_search_start}s")

    #return JSONResponse(content={"search_result": results, "nat_predictions": iNat_results})
    return JSONResponse(content={"search_result": results, "text_search_result" : [] })


# upsert an image to the index
@app.post("/upsert_image_url")
async def upsert_image_url(image_payload_request):
    return "service currently not available"

    auth_token = image_payload_request.auth_token
    if auth_token != "rosebud":
        return "not authorized"

    # get the url for the image being upserted from the request
    image_url = image_payload_request.image_url

    # make sure that it has not already been indexed
    # note that by usig "image_url in client.hash_map" instead of "image_url in client.hash_map.keys()", we can check whether the image is in index in O(1) time instead of O(n) time.
    t_hashcheck_start = time.time()
    if image_url in client.hash_map:
        return "already indexed"
    t_hashcheck_end = time.time()

    # fetch the image with an HTTP request
    t_imfetch_start = time.time()
    image = open_image_from_url(image_url)
    t_imfetch_end = time.time()

    # if the request gives us the image
    if image is not None:

        # preprocess the image for the CLIP model
        image = preprocess(image).unsqueeze(0)

        # inference the model on the image
        with torch.no_grad():
            t_encode_start = time.time()
            image_features = model.encode_image(image).squeeze()
            image_features = np.array(image_features)
            t_encode_end = time.time()

        # upsert the vector and its payload to the search client
        payload = pvs.VectorPayload(image_payload_request)    
        client.upsert(image_features, payload)


        #print(f"hash check time: {t_hashcheck_end - t_hashcheck_start}, fetch time: {t_imfetch_end-t_imfetch_start}s, encoding time: {t_encode_end - t_encode_start}s")



        # save the client 
        client.save()      
        print("client has been saved")  
        
        return "success"
    else:
        return "failure"
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=443, ssl_keyfile="/home/private.key", ssl_certfile="/home/cert.crt")
    print(f"Completed server process. {images_upserted} image features upserted to the index")

