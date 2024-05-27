import numpy as np
import vector_index
from concurrent import futures

import sys
import os

import grpc
import vector_index_pb2
import vector_index_pb2_grpc



class VectorIndexService(vector_index_pb2_grpc.VectorIndexServicer):
    '''
    
        create a gRPC service that allows a vector index to be accessed over a network
    
    '''
    def __init__(self, vector_index_path):
        self.index = vector_index.VectorIndex(vector_index_path)
        
    def Upsert(self, request, context):
        '''
        upsert a vector and payload to the index
        '''
        
        # the vector to upsert
        vector = np.frombuffer(request.nparray_bytes, dtype=np.float32)

        # get the payload
        payload = vector_index.VectorPayload(**request.payload.__dict__)

        # upsert the payload
        self.index.upsert(vector, payload)
        
        return vector_index_pb2.UpsertResponse(status="success")
    

def serve(vector_index_path):
    print("starting gRPC service")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 10))
    vector_index_service = VectorIndexService(vector_index_path)
    print(f"opened vector index at: {vector_index_path}")
    vector_index_pb2_grpc.add_VectorIndexServicer_to_server(vector_index_service,server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve('/home/cameron/Search_Engine/index_v1/vector_index/sample')
