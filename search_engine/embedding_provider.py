import page_index
import vector_index
import os
import custom_logger

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
        
        match model_name: 
            case "open_clip":
                self.open_clip_init(vector_index_path)
                self.generate_embeddings_and_upsert = self.open_clip
            
    
    def open_clip_init(self):
        import open_clip
        import torch
        import numpy as np 
        
        # load the CLIP models to encode image or text features
        self.model, _, self.preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
        self.tokenizer = open_clip.get_tokenizer('ViT-B-32')
        self.logger.log("loaded CLIP models and tokenizer")
     
        # there will be two separate indexes, one for images, and one for text 
        self.image_index = vector_index_client.VectorIndexClient(os.path.join(self.vector_index_path, f"open_clip_(image)"))
        self.text_index = vector_index_client.VectorIndexClient(os.path.join(self.vector_index_path, f"open_clip_(text)"))
        self.logger.log("Opened clients for image and text index")

    def open_clip(self, page_url: str, page_index_client : page_index.PageIndexClient):
        
        self.logger.log(f"generating embeddings for {page_url}")

        # load the page data and the images from the page index client
        page_data, image_url_list, image_list = page_index_client.retrieve_page_and_images(page_url)
        

        for i, text_section in enumerate(page_data.text_sections):
            # inference the model on the image
            with torch.no_grad():
                text_features = np.array(model.encode_text(tokenizer([text_section])).squeeze())
            
            payload = vector_index.VectorPayload(
                text_section_idx = i,
                image_url = "",
                page_url = page_url            
            )
            upsert_status = self.text_index.upsert(text_features, payload)
            self.logger.log(f"\t({i}) upserted text section, status: {upsert_status}")

        
        for i, image in enumerate(image_list): 
            # preprocess the image for the CLIP model
            image = self.preprocess(image).unsqueeze(0)

            # inference the model on the image
            with torch.no_grad():
                image_features = np.array(self.model.encode_image(image).squeeze())
            
            payload = vector_index.VectorPayload(
                text_section_idx = -1,
                image_url = image_url_list[i],
                page_url = page_url
            )
            upsert_status = self.image_index.upsert(image_features, payload)
            self.logger.log(f"\t({i}) upserted image {image_url_list[i][-50:]} status: {upsert_status}")
    



            
