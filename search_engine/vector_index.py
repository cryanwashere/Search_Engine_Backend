from pydantic import BaseModel
import uuid
import numpy as np
import pickle
import os
import sys
from dataclasses import dataclass
import hashlib
import json
from typing import List, Set
import custom_logger

import math


@dataclass
class VectorPayload:

    payload_str : str
    _id : str
    

@dataclass
class PointVector:
    vec : np.array
    payload : VectorPayload

@dataclass 
class VectorIndex:
    index : dict 

@dataclass
class VectorSearchResult:
    payload: VectorPayload
    score: float


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

        self.hash_map[payload._id] = point_vector



def hash_str(string : str):
    """
    Hashes a string using SHA-256 and returns a hexadecimal digest containing only numbers and letters.
    """
    # Generate the SHA-256 hash of the string
    hash_object = hashlib.sha256(string.encode())
    
    # Convert the hash to hexadecimal string
    hex_digest = hash_object.hexdigest()
    
    # there is no need for the hash to be giant
    return hex_digest[:10]

def directory_tree_path(input_str : str):
    '''
    given an input string, find its sub path in the directory string 
    '''
    page_url_hash = hash_str(input_str)
    page_path = "/".join(page_url_hash)
    return page_path

class UnstructuredVectorIndex:
    '''
    
        This will represent a directory, containing files of a vector index, which are going to be unstructured. The files will be pickle files, which contain a dictionary. The dictionary will map point ID strings, to PointVector objects.

        The object will store a dictionary called 'hash_map', representing the current index. As new points are upserted to the unstructured index, will be inserted into the dictionary, with their _id as the key. When the number of entries in the dictionary reaches 'file_size', the dicitionary will be saved in a pickle file, and then deleted from RAM.

        Parameters: 
            path: the path to the directory where the files will be saved
            file_size: the number of points to store in each file
    
    '''

    hash_map : dict[str, PointVector]    

    def __init__(self, path, file_size=500):

        self.hash_map = dict()

        # the number of points to store, before saving a new file
        self.file_size = file_size
        
        # check to see if anything exists at the path, and if there is nothing, make a directory where the storage will exist
        self.path = path
        if not os.path.isdir(path):
            print(f"No unstructured vector index found, creating new one at: {self.path}")
            os.mkdir(path)
        else:
            print(f"found unstructured vector index at: {self.path}")

    def upsert(self, point: PointVector):
        # insert the point into the hash_map
        self.hash_map[point.payload_id] = point

        if len(self.hash_map.keys()) >= self.file_size:
            self.save()
    
    def save(self):
        '''
        write the hash map to a file, and then delete the contents of the hash map
        '''

        # choose a path to store the directory tree
        tree_path = directory_tree_path(str(uuid.uuid1))

        # join it to the full tree path
        full_tree_path = os.path.join(self.path, tree_path)

        print(f"saving file in unstructured index to: {full_tree_path}")
        # save the file the hash map to a file 
        with open(full_tree_path, 'wb') as f:
            pickle.dump(self.hash_map, f)
            f.close()
        
        # clear out the hash map 
        self.hash_map = dict()













@dataclass
class PointGraphNode:
    point: PointVector
    # maps the level, to a set containing the ids of all the neighbors on that level 
    neighbors: dict[int, Set[str]]

class PointGraph: 
    def __init__(self, path):
        self.path = path 
    def insert(self, point: PointVector):
        new_node = PointGraphNode(
            point=point, 
            neighbors=None
        )
    def SELECT_NEIGHBORS_SIMPLE(q, C, M):
        '''
        Parameters: 
            q: base element
            C: Candidate elements
            M: number of neighbors to return
        '''
        pass
        

class VectorIndexNode: 
    pass 

@dataclass
class VectorIndexAtlas: 
    '''
    Store the a 'map' of the vector grid
    '''

    pass


class VectorIndex:
    '''

    A python object used to represent a vector index 

    Args:
        path: the path to the root directory of the search client 

        (if an index does not already exist at 'path'):
            dim: int
            distance_metric: str
            tree_split: int
    


    Here is how the directory that the vector index represents should be structured: 

    path:
        atlax.pkl
        storage:
            

    
    '''
    def __init__(self, path, **kwargs):
        
        # storage for the vectors
        self.unstructured_index_path = os.path.join(path, "unstructured_index")


        


    @staticmethod
    def dot_product_transform(vector: np.array) -> np.array:
        '''
        Transformation is applied to a vector, so that distance comparison becomes equivalent to dot product comparison

        Source: 
        https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/XboxInnerProduct.pdf
        '''
        g = np.linalg.norm(index, axis=1)
        _max = g.max()
        g = np.sqrt((1000 ** 2) - (g ** 2))
        g = np.expand_dims(g, axis=-1)
        index_2 = np.concatenate((g, index), axis = 1)   

    def transform(vector: np.array) -> np.array:
        '''
        depending on whatever distance metric is being used, the vectors will be transformed, so that a kNN will yield the correct results given their metric

        cosine: 
            the vector is normalized

        dot product: 
            the special dot product transform is applied to the vector

        euclidean: 
            nothing happens
        '''
        pass
    
    def insert(self, vector: np.array):
        pass
        
    def query(self, q: np.array, k: int = 5):
     pass

        
    



if __name__ == "__main__":
    

    client = VectorIndex(
        "/tmp/test_index_2",
        dim = 512,
        distance_metric = 'euclidean',
        tree_split = 100
    ) 
    # display logs for testing
    client.logger.verbose = True

    for i in range(100000):
        v = np.random.randn(512)
        client.insert(v)
    
    q = np.random.randn(512)

    client.query(q)