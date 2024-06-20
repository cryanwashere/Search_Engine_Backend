import vector_index_client
from PIL import Image
import embedding_provider
import vector_index
from typing import List

class SearchEngineClient:
    '''
    
        The functionality of the search engine
    
    '''
    def __init__(self, 
            vector_index_path,
            page_index_path,
        ):

        self.vector_index_path = vector_index_path
        self.page_index_path = page_index_path

        # load the vector index clients
        self.open_clip_image_client = vector_index_client.VectorIndexClient("open_clip_image", hostname="localhost")

        self.snowflake_arctic_s_client = vector_index_client.VectorIndexClient("snowflake_arctic_s", hostname="localhost")

        # load the embedding providers
        self.open_clip_embedding_provider = embedding_provider.EmbeddingProvider("open_clip")

        self.snowflake_arctic_s_embedding_provider = embedding_provider.EmbeddingProvider("snowflake_arctic_s")
    
    def search_image(self, image: Image) -> List[vector_index.SearchResult]:
        image_embedding = self.open_clip_embedding_provider.open_clip_embed_image(image)
        return self.open_clip_image_client.search(image_embedding)

    def search_text(self, text: str) -> List[vector_index.SearchResult]:

        text_embedding = self.snowflake_arctic_s_embedding_provider.embed_text(text)

        return self.snowflake_arctic_s_client.search(text_embedding)
        

if __name__ == "__main__":
    pass