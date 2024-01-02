import open_clip

import torch
import numpy as np
from PIL import Image
import io
import os

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse

# load the model and tokenizer
model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
tokenizer = open_clip.get_tokenizer('ViT-B-32')
print("loaded model and tokenizer")





app = FastAPI()




@app.post("/search_image")
async def search_image(file: UploadFile = File(...)):
    image = await file.read()
    #print("read file")
    image = Image.open(io.BytesIO(image))
    #print("opened image")

    # preprocess the Pillow image
    image = preprocess(image).unsqueeze(0)
    #print("ran preprocess on image")

    # inference the model on the image
    with torch.no_grad():
        image_features = model.encode_image(image).squeeze()
    #print("generated image features")

    return JSONResponse(content={"search_result": image_features)
    
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.0", port=8001)

