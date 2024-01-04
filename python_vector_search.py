
from pydantic import BaseModel
import uuid
import numpy as np
import pickle
import os

class ImagePayloadRequest(BaseModel):
    image_url: str
    page_url: str

class VectorPayload:
    def __init__(self, payload_request: ImagePayloadRequest):
        self.image_url = payload_request.image_url
        self.page_url = payload_request.page_url
    def json(self):
        return {
            "image_source" : self.image_url,
            "page_source" : self.page_url,
            "type" : "image"
        }

class PointVector:
    def __init__(self, vector, payload: VectorPayload):
        self.vec = vector
        self.payload = payload

class VectorSearchResult:
    def __init__(self, payload, score):
        self.payload = payload
        self.score = score


class VectorSearchClient:
    def __init__(self, client_path):

        # path to where the index is stored
        self.client_path = client_path

        # load the search client
        if not os.path.isfile(client_path):
            print("could not find existing index file (creating new index)")
            self.hash_map = dict()
        else:
            with open(client_path, "rb") as f:
                self.hash_map = pickle.load(f)
            print(f"opened search client with {self.point_count()} points")
    
    def save(self):
        # save the search client
        with open(self.client_path, 'wb') as f:
            pickle.dump(self.hash_map, f)
            f.close()
    

    def point_count(self):
        # get the number of points that the search client contains
        return len(self.hash_map.values())

    def upsert(self, vector, payload: VectorPayload):
        

        # create the point vector
        point_vector = PointVector(vector, payload)

        # insert the point into the vector storage
        self.hash_map[payload.image_url] = point_vector
    
    def search(self, query_vector, k=20):
        results = list()

        for (id, point_vector) in self.hash_map.items(): 
            score = point_vector.vec @ query_vector

            results.append(VectorSearchResult(point_vector.payload, score))
        
        results = sorted(results, key = lambda x: x.score, reverse=True)
        
        #print([r.score for r in results])

        return results[:k]
            
