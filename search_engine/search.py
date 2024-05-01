import python_vector_search as pvs
import search.dictionary_search as di

class SearchClient:
    '''
    
        The functionality of the search engine
    
    '''
    def __init__(self, 

            image_vector_client_path, 
            text_vector_client_path, 
            page_lookup_client_path

        ):
        
        # a search client for image embeddings
        self.image_vector_client = pvs.VectorSearchClient(image_vector_client_path)

        # a search client for text embeddings
        self.text_vector_client = pvs.VectorSearchClient(text_vector_client_path)

        # a lookup to map urls to important data about their contents
        self.page_lookup_client = di.PageLookupClient(page_lookup_client_path)