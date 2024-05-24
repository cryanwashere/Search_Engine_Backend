import page_index
import vector_index
import os

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
        print("loaded CLIP models and tokenizer")

        # there will be two separate indices, one for images, and one for text 
        self.image_index = vector_index.VectorIndexClient(os.path.join(self.vector_index_path, f"{self.model_name}_(image)"))
        self.text_index = vector_index.VectorIndexClient(os.path.join(self.vector_index_path, f"{self.model_name}_(text)"))

    def open_clip(self, page_url: str, page_index_client : page_index.PageIndexClient):

        # load the page data and the images from the page index client
        page_data, image_list = page_index_client.retrieve_page_images(page_url)

        for text_section in page_data.text_sections:
            # inference the model on the image
            with torch.no_grad():
                text_features = np.array(model.encode_text(tokenizer([text_section])).squeeze())

        
        for image in image_list: 
            # preprocess the image for the CLIP model
            image = self.preprocess(image).unsqueeze(0)

            # inference the model on the image
            with torch.no_grad():
                image_features = np.array(self.model.encode_image(image).squeeze())
            