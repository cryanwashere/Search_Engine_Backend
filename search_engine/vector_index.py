import numpy as np
import pickle
import os
import sys
from dataclasses import dataclass
import dataclasses
import json
import custom_logger
from sqlitedict import SqliteDict
import ngtpy




@dataclass
class VectorPayload:

    # if the vector represents a text section, the index of the text section in the page data where the text section comes from
    text_section_idx :int

    # if the vector represents an image, the url of the image
    image_url : str

    # the page url that the content was sourced from
    page_url : str 

    def dict(self):
        return dataclasses.asdict(self)
    
    @staticmethod
    def from_proto(proto):
        return VectorPayload(
            text_section_idx = proto.text_section_idx,
            image_url = proto.image_url,
            page_url = proto.page_url
        )


@dataclass
class SearchResult:
    payload : VectorPayload
    score : float




class VectorIndex:
    '''

    A class that manages the vector index
    
    '''
    def __init__(self, path, **kwargs):

        self.path = path
        if not os.path.isdir(path):
            print(f"no vector index directory found at: {path}. making new one")
            os.mkdir(self.path)

        # the path to where the NGT client is stored
        self.ngt_index_path = os.path.join(path, "ngt_index")
        if not os.path.isdir(self.ngt_index_path):
            print(f"no NGT index found at: {self.ngt_index_path}. making new one")

            dimension = dimension=kwargs['dimension']
            distance_type = kwargs['distance_type']

            print(f"making NGT client with dimension: {dimension} and distance type: {distance_type}")

            # create a new NGT index at the given directory
            ngtpy.create(path=self.ngt_index_path, dimension=dimension ,distance_type=distance_type)
        # open the index
        self.ngt_index = ngtpy.Index(self.ngt_index_path)

        # the path to where the ID map gets stored
        self.id_map_path = os.path.join(path, "id_map.sqlite")
        # create a connection to the database dictionary where the id map should be stored
        # the id map maps the ids of vectors to their payloads
        self.id_map_db = SqliteDict(self.id_map_path)


        # this is for counting how many vectors have been upserted since the object was initialized
        self.upsert_counter = 0
    
    def upsert(self, vector: np.array, payload: VectorPayload):
        # insert the id into the NGT Index
        point_id = self.ngt_index.insert(vector)

        # save the payload of the vector to the payload dictionary
        self.id_map_db[point_id] = payload.dict()

        # count the upsert
        self.upsert_counter += 1


        # every 500 upserts, perform a checkpoint
        if self.upsert_counter % 500 == 0:
            self.checkpoint()
    
    def search(self, query: np.array, size: int = 10):
        ngt_results = self.ngt_index.search(query, size=size)
        
        search_results = list()
        for (point_id, score) in ngt_results:
            search_results.append(SearchResult(
                payload = VectorPayload(**self.id_map_db[point_id]),
                score = score
            ))
        return search_results


    def checkpoint(self):
        # nescessary for the inserted vectors to be searchable
        self.ngt_index.build_index()
        self.ngt_index.save()
        self.id_map_db.commit()
    
    def save(self):
        self.ngt_index.save()
    
    def close(self):
        self.ngt_index.close()
        self.id_map_db.close()

    def finish(self):
        self.checkpoint()
        self.save()
        self.close()



        
if __name__ == "__main__":
    
    
    if sys.argv[1] == "create":
            new_index_name = sys.argv[2]
            new_index_dim = int(sys.argv[3])
            new_index_distance_type = sys.argv[4]

            VectorIndex(
                f'/home/cameron/Search_Engine/index_v1/vector_index/{new_index_name}',
                dimension = new_index_dim,
                distance_type = new_index_distance_type
            )
    