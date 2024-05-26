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
from sqlitedict import SqliteDict
import math


@dataclass
class VectorPayload:

    # if the vector represents a text section, the index of the text section in the page data where the text section comes from
    text_section_idx :int

    # if the vector represents an image, the url of the image
    image_url : str

    # the page url that the content was sourced from
    page_url : str 
    




class VectorIndex:
    '''

    A class that manages the vector index
    
    '''
    def __init__(self, path, **kwargs):

        self.path = path
        if not os.path.isdir(path):
            print(f"no vector index directory found at: {path}. making new one")

        # the path to where the NGT client is stored
        self.ngt_index_path = os.path.join(path, "ngt_index")
        if not os.path.isdir(self.ngt_index_path):
            print(f"no NGT index found at: {self.ngt_index_path}. making new one")

            # create a new NGT index at the given directory
            ngtpy.create(path=bytes(self.ngt_index_path), dimension=kwargs['dimension'], distance_type=kwargs['distance_type'])
        # open the index
        self.ngt_index = ngtpy.Index(self.ngt_index_path)

        # the path to where the ID map gets stored
        self.id_map_path = os.path.join(path, "id_map.sqlite")
        # create a connection to the database dictionary where the id map should be stored
        # the id map maps the ids of vectors to their payloads
        self.id_map_db = SqliteDict(self.id_map_path)


        
        