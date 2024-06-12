import python_vector_search as pvs
import search.dictionary_search as di
from PIL import Image

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

        # 
    
    def search_image(self, image: Image):
        pass
    def search_text(self, text: str):
        pass