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


class VectorIndexClient:
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