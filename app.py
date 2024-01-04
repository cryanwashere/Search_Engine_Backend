import open_clip

import torch
import numpy as np
from PIL import Image
import io
import json

from torchvision import transforms
import torchvision
from torch import nn

import requests

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse


import python_vector_search as pvs
client = pvs.VectorSearchClient("index/cli_dict.pkl")




iNat_state_dict = torch.load('/Users/cameronryan/Desktop/projects/Naturify/model_state_dict_finished.pth', map_location=torch.device('cpu'))
iNat_model = torchvision.models.vit_b_16()
iNat_model.heads = nn.Sequential(
    nn.Linear(in_features=iNat_model.heads[0].in_features, out_features = 10000)
)
iNat_model.load_state_dict(iNat_state_dict)
iNat_model.eval()
# I don't know if this is nescessary
del iNat_state_dict
print("loaded Naturify model")




with open("categories.json","r") as f:
    iNat_categories = json.load(f)

iNat_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
def iNat_inference(inp):
    out =iNat_model(inp)
    out = torch.softmax(out, dim=1)
  
    vals, idxs = torch.topk(out, 5, dim=1)

    predictions = list()
    for idx in idxs.squeeze():
        predictions.append({
            "species" : iNat_categories[idx],
            "score" : out.squeeze()[idx].item(),
        })
    return predictions



model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
tokenizer = open_clip.get_tokenizer('ViT-B-32')
print("loaded CLIP model and tokenizer")

with torch.no_grad():
    special_keys = ["a plant", "an animal", "fungi", "a mushroom", "an insect", "a bird"]
    special_key_vecs = model.encode_text(tokenizer(special_keys))


app = FastAPI()


def open_image_from_url(url):
    try:
        # Send a GET request to the URL and get the image content
        response = requests.get(url)
        response.raise_for_status()  # Check for errors in the HTTP response

        # Open the image using Pillow and BytesIO
        image = Image.open(io.BytesIO(response.content))
        return image
    
    except Exception as e:
        return None


@app.get("/search",response_class=HTMLResponse)
async def search():
    with open("search_page.html","r") as f:
        return f.read()

@app.post("/search_image")
async def search_image(file: UploadFile = File(...)):
    image = await file.read()
    #print("read file")
    pil_image = Image.open(io.BytesIO(image))

    # preprocess the Pillow image
    image = preprocess(pil_image).unsqueeze(0)

    # inference the model on the image
    with torch.no_grad():
        image_features = model.encode_image(image).squeeze()

        special_key_scores = image_features @ special_key_vecs.T
        #for i, score in enumerate(special_key_scores):
        #    print(f"{special_keys[i]}: {score}")
        
        if max(special_key_scores) > 18:
            iNat_results = iNat_inference(iNat_transform(pil_image).unsqueeze(0))
        else:
            iNat_results = []


        image_features = np.array(image_features)
    
    results = client.search(image_features)
    results = [r.payload.json() for r in results]

     
    return JSONResponse(content={"search_result": results, "nat_predictions": iNat_results})



@app.post("/upsert_image_url")
async def upsert_image_url(image_payload_request: pvs.ImagePayloadRequest):

    image_url = image_payload_request.image_url

    if image_url in client.hash_map:
        return "already indexed"

    # fetch the image 
    image = open_image_from_url(image_url)

    if image is not None:

        # preprocess the image for the clip model
        image = preprocess(image).unsqueeze(0)

        # inference the model on the image
        with torch.no_grad():
            image_features = model.encode_image(image).squeeze()
            image_features = np.array(image_features)

        # upsert the vector and its payload to the search client
        payload = pvs.VectorPayload(image_payload_request)    
        client.upsert(image_features, payload)

        client.save()
        
        
        return "success"
    else:
        return "failure"
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

