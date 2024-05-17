
from pydantic import BaseModel
import uuid
import numpy as np
import pickle
import os
import sys
from dataclasses import dataclass
import hashlib
import json
from typing import List
import custom_logger

import math


@dataclass
class VectorPayload:

    image_url : str
    page_url : str
    _id : str
    
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


def hyperspherical_coordinates(x):
    """
    Calculate angular coordinates of the vectors in `x` along the first axis.

    Source:
    https://en.wikipedia.org/wiki/N-sphere#Spherical_coordinates
    """
    a = x[1:] ** 2
    b = np.sqrt(np.cumsum(a[::-1], axis=0))
    phi = np.arctan2(b[::-1], x[:-1])
    phi[-1] *= np.sign(x[-1])
    return phi

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


@dataclass
class AtlasNode: 

    # a uuid representing the node 
    _id : str
    
    # Is the following node a leaf:
    is_leaf : bool 

    # if the node is a leaf, then this is where the file containing the node's vectors are stored. 
    #file_path : str
    # for testing when nothing is saved to disk
    bucket : list

    # maps the hash of each distance in distances (converted to a string), to the id of the child node that corresponds to the distance
    distance_codebook : dict[str, str]
    # distances between each of the child nodes, and the current node's centroid
    distances : np.array

    # if the node is not a leaf, then this is a dict containing all of the child nodes. 
    child_nodes : dict[str, object]

    # the vector representing the node's centroid. allows the node to be compared to other nodes 
    centroid : np.array 

    '''
    Creates a new child node with 'vec' as its centroid
    
    Note that this merely completes the process of adding the child node (and allowing it to be found). it does not ensure that the parent node has less than 'tree_split' many child nodes
    '''
    def add_child(self, vec: np.array): 
        # create the new child node of this node 
        new_child_node_id = str(uuid.uuid1())
        new_child_node = AtlasNode(
            _id = new_child_node_id,
            is_leaf = True, 
            bucket = list(),
            distance_codebook = dict(),
            distances = np.array([]), 
            child_nodes = dict(),
            centroid = vec
        )

        # add the child node to the child node dictionary
        self.child_nodes[new_child_node_id] = new_child_node

        # find the distance between the child node's centroid, and this node's centroid
        d = float(np.sqrt(((vec - self.centroid) ** 2).sum()))
        
        # append this distance to the list of distances
        self.distances = np.append(self.distances, d)

        # find the hash for the distance float
        d_hash = hashlib.sha256(str(d).encode()).hexdigest()

        # insert the hash of the distance into this node's codebook, mapping to the new child node's id
        self.distance_codebook[d_hash] = new_child_node_id

    '''
    Parameters:
        is_leaf: bool 
        centroid: np.array
    '''
    @staticmethod
    def root_init(dim):

        node = AtlasNode(
            _id = str(uuid.uuid1()), 
            bucket = list(),
            distance_codebook=dict(),
            distances=np.array([]), 
            child_nodes=dict(), 
            is_leaf=True,
            centroid=np.zeros(dim) # the first root node will be at the origin
        )
        return node
        


def find_distance_hash(distance: float, node: AtlasNode):
    differences = np.abs(node.distances - distance)
    min_difference_idx = np.argsort(differences)[0]
    min_distance = node.distances[min_difference_idx]
    min_distance_hash = hashlib.sha256(str(min_distance).encode()).hexdigest()
    return node.distance_codebook[min_distance_hash]

@dataclass
class VectorIndexAtlas: 
    '''
    Store the a 'map' of the vector grid
    '''

    # the root of the storage tree
    root: AtlasNode

    # the total number of points in the index
    point_count : int

    # the dimension of the vector index
    dim : int 

    # a string representing what type of distance the atlas uses. 
    # options are: 'euclidean', 'cosine', 'dot_product'
    distance_metric : str

    # defines how many points can be at a node until the tree splits
    tree_split : int

    '''
    Parameters: 
        dim,
        distance_metric, 
        tree_split
    '''
    def __init__(self, **kwargs):
        self.point_count = 0
        self.root = AtlasNode.root_init(dim=kwargs['dim'])

        self.__dict__.update(kwargs)


class VectorIndex:
    '''

    A python object used to represent a vector index 

    Args:
        path: the path to the root directory of the search client 

        (if an index does not already exist at 'path'):
            dim: int
            distance_metric: str
            tree_split: int
    
    '''
    def __init__(self, path, **kwargs):
        
        self.path = path
        self.atlas_path = os.path.join(path, "atlas.pkl")
        self.storage_path = os.path.join(path, "storage")


        # if the directory where the index is intended to be stored does not exist, then create a new index directory
        if not os.path.isdir(self.path):
            # create the directory where the index will be stored
            os.mkdir(self.path)
            # we also assume that if there is no atlas, than the index is new, so we create the storage directory
            os.mkdir(self.storage_path)


        # check if the atlas exists. if the atlas does not exist, then this is a new vector client, and a new atlas needs to be created. 
        # the atlas is saved as a python pickle object
        if not os.path.isdir(self.atlas_path):
            print(f"creating new index at: {self.path}")

            # initialize the atlas 
            self.atlas = VectorIndexAtlas(
                dim = kwargs['dim'],
                distance_metric = kwargs['distance_metric'],
                tree_split = kwargs['tree_split']
            )
            

        # if the atlas does exist, then open the atlas
        else: 
            print(f"found index at {self.path}")
            with open(self.atlas_path,"rb") as f:
                self.atlas = pickle.load(f)

        

        # simple logging
        self.logger = custom_logger.Logger()


        # just for testing
        self.all_vectors = list()


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
        '''
        insert the vector into the index
        '''

        self.all_vectors.append(vector)


        # start the search with the root node
        node = self.atlas.root

        # iteratively navigate the tree to find where the node is supposed to be 
        while not node.is_leaf: 
            # find the distance between the vector and the the node's point 
            r = np.sqrt(((vector - node.centroid) ** 2).sum())

            # find the bucket where the vector is supposed to be 
            r_hash = find_distance_hash(r, node)

            # proceed to the next node in the tree
            node = node.child_nodes[r_hash]

        else: 
            # is the bucket full? 
            if len(node.bucket) + 1 >= self.atlas.tree_split:
                self.logger.log(f"bucket is full. creating new bucket for {node._id}. (bucket currently contains: {len(node.bucket)} points)")

                # if the bucket is full, then make a new child node for each of the vectors in the bucket (there should be self.atlas.tree_split child nodes)
                for vec in node.bucket + [vector]:
                    # create a child node for the node, with the vector as it's centroid
                    node.add_child(vec)    
                
                # make sure that the node is not a leaf
                node.is_leaf = False

                # keep the bucket for now. 
                #node.bucket = None

            # if the bucket is not full, then add the node to the bucket
            else:
                node.bucket.append(vector)
        
    def query(self, q: np.array, k: int = 5):
        # start the search with the root node
        node = self.atlas.root

        depth = 0 

        # iteratively navigate the tree to find where the node is supposed to be 
        while not node.is_leaf: 
            # find the distance between the vector and the the node's point 
            r = np.sqrt(((q - node.centroid) ** 2).sum())

            # find the bucket where the vector is supposed to be 
            r_hash = find_distance_hash(r, node)

            # ensure that the child node does not have any empty bucket
            if len(node.child_nodes[r_hash].bucket) <= 0:
                break
            else: 
                # proceed to the next node in the tree
                node = node.child_nodes[r_hash]
                depth += 1

        # the node is a leaf 
        self.logger.log(f"reached leaf node. bucket contains: {len(node.bucket)} points")
        bucket_distances = np.sqrt(((q - np.array(node.bucket)) ** 2).sum(axis=1))
        
        self.logger.log(f"depth: {depth}, distances: {bucket_distances.shape}")
        
        sorted_idx = np.argsort(bucket_distances)

        topk = bucket_distances[sorted_idx[:k]]

        print(f"distances of closest points: {topk}")

        all_distances = np.sqrt(((q - np.array(self.all_vectors)) ** 2).sum(axis=1))
        print(f"(brute force) distances of closest point: {all_distances[np.argsort(all_distances)[:k]]}")

        print(f"distance of farthest point: {all_distances[np.argsort(all_distances)[-1]]}")


        
    



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