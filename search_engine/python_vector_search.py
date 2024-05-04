
from pydantic import BaseModel
import uuid
import numpy as np
import pickle
import os
import sys
from tqdm import tqdm
from dataclasses import dataclass

@dataclass
class VectorPayload:
    page_id : str
    image_url : str
    page_url : str
    text_section_id : str

    def json(self):
        return self.__dict__
    

@dataclass
class PointVector:
    vec : np.array
    payload : VectorPayload


@dataclass 
class VectorIndex:
    index : dict 

@dataclass
class VectorSearchResult:
    def __init__(self, payload, score):
        self.payload = payload
        self.score = score



class VectorSearchClient:
   
    def directory_client(self, index_dir):
        '''
        
            The vector search client represents a directory. To be used for deployment
        
        '''
        self.index_dir = index_dir

        # the following code is going to open each of the index files in the given directory, and merge them into one 


        self.hash_map = dict()

        clients = os.listdir(index_dir)
        clients = list(filter(lambda x : x[-3:] == 'pkl', clients))
        print(f"merging clients: {clients}")
        
        for client_file in clients: 
            client_path = os.path.join(index_dir, client_file)


            # this is kind of crazy
            sys.path.append(r'/home/volume/Search_Engine_Backend/search_engine')            
            # open the client using python pickle
            with open(client_path, "rb") as f:

                #print(client_path)
                client_index = pickle.load(f)
            
            print(f"{client_file}: {len(client_index.keys())} points")

            # merge the index from the currently iterated client with the combined index
            self.hash_map.update(client_index)

            # just in case memory is a problem here
            del client_index
        

        print(f"completed merging index. merged index contains: {len(self.hash_map.keys())} points")

        return self


    def file_client(self, index_path):
        ''' 

            The vector search client represents a single file. To be used for indexing 

        '''

        self.index_path = index_path 

        # load the search client
        # if nothing exists in the client path, it will create a new index. Otherwise it will load the existing index
        if not os.path.isfile(index_path):
            print(f"could not find existing index file (creating new index at path {self.index_path})")
            self.hash_map = dict()
        else:
            with open(index_path, "rb") as f:
                self.hash_map = pickle.load(f)
            print(f"opened search client with {self.point_count()} points")
        
        return self

        
    
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
        if payload.image_url != '':
            self.hash_map[payload.image_url] = point_vector
        else:
            self.hash_map[payload.text_section_id] = point_vector


# testing
if __name__ == "__main__": 

    print("running test for python_vector_search.py")
    #client_path = sys.argv[1]
    client_path = "/home/volume/index/vector_index/image"

    # load the vector search client
    client = VectorSearchClient().directory_client(client_path)
    # create a point matrix for the search client
    client.create_point_matrix()