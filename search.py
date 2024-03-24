import python_vector_search as pvs

class SearchClient:
    def __init__(self, vector_client_path):
        self.vector_client_path = vector_client_path
        self.vector_client = pvs.VectorSearchClient(vector_client_path)