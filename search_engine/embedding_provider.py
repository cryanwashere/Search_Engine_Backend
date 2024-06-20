import page_index
import os
import custom_logger
import torch
import numpy as np
import open_clip
import vector_index_client
import vector_index
from PIL import Image
from sentence_transformers import SentenceTransformer



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

    def __init__(self, model_name):
        self.model_name = model_name

        self.logger = custom_logger.Logger("EmbeddingProvider")
        self.logger.verbose = True
        
        # here models will be loaded based on which model has been selected. this makes it easy to standardize the usage of different models
        if model_name == "open_clip":
            self.open_clip_init()
            self.generate_embeddings_and_upsert = self.open_clip
            self.checkpoint = self.open_clip_checkpoint
            self.embed_image = self.open_clip_embed_image
        if model_name == "snowflake_arctic_s":
            self.snowflake_arctic_s_init()
            self.generate_embeddings_and_upsert = self.snowflake_arctic_s
            self.checkpoint = self.snowflake_arctic_checkpoint
            self.embed_text = self.snowflake_arctic_s_embed_text

    '''
    METHODS FOR OPEN CLIP
    '''
    
    def open_clip_init(self):
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
    
    '''
    METHODS FOR SNOWFLAKE ARTIC S
    '''

    def snowflake_arctic_s_init(self):
        self.model = SentenceTransformer("Snowflake/snowflake-arctic-embed-s")
        self.index = vector_index_client.VectorIndexClient("snowflake_arctic_s")

        self.logger.log("Loaded model and vector index client")
    
    def snowflake_arctic_s_embed_text(self, text: str) -> np.array:
        document_embeddings = self.model.encode(text).squeeze()
        document_embeddings = np.array(document_embeddings)
        return document_embeddings

    def snowflake_arctic_s(self, page_url: str, page_index_client: page_index.PageIndexClient):
        page_data = page_index_client.retrieve_page_data(page_url)

        if page_data is None: 
            self.logger.error(f"failed to load page data for url: {page_url}")
            return 

        text_sections = page_data.text_sections

        if len(text_sections) <= 0:
            self.logger.log("page does not have any viable text sections, moving on.")
            return
    
        document_embeddings = self.model.encode(text_sections)
        
        document_embeddings = np.array(document_embeddings)

        for i, embedding in enumerate(document_embeddings):

            assert embedding.dtype == np.float32

            payload = vector_index.VectorPayload(
                text_section_idx=i,
                image_url='',
                page_url=page_url
            )
            upsert_status = self.index.upsert(embedding, payload)
            self.logger.log(f"\t({i}) Upserted text embedding. Status: {upsert_status}")

    def snowflake_arctic_checkpoint(self):
        self.index.checkpoint()








# testing     
if __name__ == "__main__":
    embedding_provider = EmbeddingProvider("snowflake_arctic_s")

    page_index_client = page_index.PageIndexClient("/home/cameron/Search_Engine/index_v1/page_index")

    embedding_provider.generate_embeddings_and_upsert('https://en.wikipedia.org/wiki/!!!', page_index_client)