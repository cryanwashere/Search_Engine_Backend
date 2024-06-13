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
        self.open_clip_image_client = vector_index_client.VectorIndexClient("open_clip_image")

        # load the embedding providers
        self.open_clip_embedding_provider = embedding_provider.EmbeddingProvider("open_clip")
    
    def search_image(self, image: Image) -> List[vector_index.SearchResult]:
        image_embedding = self.open_clip_embedding_provider.open_clip_embed_image(image)
        return self.open_clip_image_client.search(image_embedding)

    def search_text(self, text: str) -> List[vector_index.SearchResult]:
        pass

if __name__ == "__main__":
    client = SearchEngineClient()