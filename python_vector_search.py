
from pydantic import BaseModel
import uuid
import numpy as np
import pickle
import os
from tqdm import tqdm
from dataclasses import dataclass

class ImagePayloadRequest(BaseModel):
    image_url: str
    page_url: str
    auth_token: str

@dataclass
class VectorPayload:
    page_id : str
    image_url : str
    page_url : str
    

@dataclass
class PointVector:
    vec : np.array
    payload : VectorPayload


@dataclass 
class VectorIndex:
    index : dict 

class VectorSearchResult:
    def __init__(self, payload, score):
        self.payload = payload
        self.score = score



class VectorSearchClient:
    def __init__(self, index_path):

        self.index_path = index_path

        # load the search client
        # if nothing exists in the client path, it will create a new index. Otherwise it will load the existing index
        if not os.path.isfile(index_path):
            print("could not find existing index file (creating new index)")
            self.index = dict()
        else:
            with open(index_path, "rb") as f:
                self.index = pickle.load(f)
            print(f"opened search client with {self.point_count()} points")

        
    
    def create_point_matrix(self):
        # put all of the points from the index into one NumPy matrix. This way, in order to search the database, it can all be done with one matrix-vector product in NumPy, which is much faster than computing every one individually


        self.data_points = list(self.hash_map.values())
        
        self.point_matrix = list(map(lambda x: x.vec, self.data_points))
        self.point_matrix = np.array(self.point_matrix)
        
        print(f"created point matrix for vector search client {self}")
    


    # More efficient search, which does the similarity computation as a numpy matrix-vector product
    def search2(self, query_vector, k=20):
        # NumPy matrix-vector product
        scores = self.point_matrix @ query_vector

        # get the indices of the highest values
        sorted_score_indices = np.argsort(scores)[-k:]

        results = []
        for index in sorted_score_indices:

            # How do we get the point vector?
            point_vector = self.data_points[index]
            results.append(VectorSearchResult(point_vector.payload, scores[index]))

        # Sort the results so that they are not in reverse order of score
        results = sorted(results, key = lambda x: x.score, reverse=True)
        return results[:k]

    
    def save(self):

        
        # save the search client
        with open(self.index_path, 'wb') as f:
            pickle.dump(self.hash_map, f)
            f.close()

    def point_count(self):
        # get the number of points that the search client contains
        return len(self.hash_map.values())

    def search(self, query_vector, k=5):

        results = list()
        for (id, point_vector) in self.hash_map.items(): 
            score = point_vector.vec @ query_vector

            results.append(VectorSearchResult(point_vector.payload, score))
        
        results = sorted(results, key = lambda x: x.score, reverse=True)
        
        #print([r.score for r in results])

        return results[:k]

    def upsert(self, vector, payload: VectorPayload):
        # upssert an image and a payload into the search index

        # create the point vector
        point_vector = PointVector(vector, payload)

        # insert the point into the vector storage
        self.hash_map[payload.image_url] = point_vector


if __name__ ==