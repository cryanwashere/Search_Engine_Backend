import page_index
import os
import custom_logger
import torch
import numpy as np
import open_clip
import vector_index_client
import vector_index
from PIL import Image


class EmbeddingProvider:

    '''
    This class will be used to generate embeddings. It is initialized with the name of a specific model, and it will load that model for use. 

    Parameters: 
        model_name: the name of the model that is being used
        vector_index_path: the path to the root directory of the vector index.
 

    Public Methods: 
        generate_embeddings_and_upsert:
            given the way that the EmbeddingProvider has been initialized, create generate embeddings for whatever page content the models use, and then upsert them to their vector clients. 
    '''

    def __init__(self, model_name, vector_index_path):
        self.model_name = model_name
        self.vector_index_path = vector_index_path

        self.logger = custom_logger.Logger("EmbeddingProvider")
        self.logger.verbose = True
        
        # here models will be loaded based on which model has been selected. this makes it easy to standardize the usage of different models
        if model_name == "open_clip":
            self.open_clip_init(vector_index_path)
            self.generate_embeddings_and_upsert = self.open_clip
            self.checkpoint = self.open_clip_checkpoint
            
    
    def open_clip_init(self, vector_index_path: str):
        # load the CLIP models to encode image or text features
        self.model, _, self.preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
        self.tokenizer = open_clip.get_tokenizer('ViT-B-32')
        self.logger.log("loaded CLIP models and tokenizer")

        # there will be two separate indices, one for images, and one for text 
        self.image_index = vector_index_client.VectorIndexClient("open_clip_image")
        self.text_index = vector_index_client.VectorIndexClient("open_clip_text")
        self.logger.log("opened vector index clients")
    
    def open_clip_checkpoint(self):
        self.image_index.checkpoint()

    def open_clip_embed_image(self, image: Image) -> np.array:
        ''' Generate a feature vector for an image, with the Open Clip model '''
        try: 
            # preprocess the image for the CLIP model
            image = self.preprocess(image).unsqueeze(0)
        except Exception as e: 
            self.logger.error(f"failed to process image with error: {e}")
            return None 

        # inference the model on the image
        with torch.no_grad():
            image_features = np.array(self.model.encode_image(image).squeeze())

        return image_features
        


    def open_clip(self, page_url: str, page_index_client: page_index.PageIndexClient):
        self.logger.log(f"generating embeddings for images in {page_url}")

        try:
            # load the page data and the images from the page index client
            page_data, image_url_list, image_list = page_index_client.retrieve_page_and_images(page_url)
        except Exception as e:
            self.logger.error(f"failed to load page data for {page_url} with error: {e}")
            return
            
        for i, image in enumerate(image_list): 

            image_features = self.open_clip_embed_image(image)

            # ensure that the image embeddings were successful
            if image_features is None : continue
            
            assert image_features.dtype == np.float32

            payload = vector_index.VectorPayload(
                text_section_idx = -1,
                image_url = image_url_list[i],
                page_url = page_url
            )

            upsert_status = self.image_index.upsert(image_features, payload)
            self.logger.log(f"\t({i}) upserted image embedding {image_url_list[i][-50:]} status: {upsert_status}")



# testing     
if __name__ == "__main__":
    embedding_provider = EmbeddingProvider("open_clip","/project-dir/index_v1/vector_index")

    page_index_client = page_index.PageIndexClient("/project-dir/index_v1/page_index")

    embedding_provider.generate_embeddings_and_upsert('https://en.wikipedia.org/wiki/Rabbit', page_index_client)