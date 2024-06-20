import numpy as np
import vector_index
from concurrent import futures

import sys
import os

import grpc
import vector_index_pb2
import vector_index_pb2_grpc
import index_network_config



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

        try:
            # the vector to upsert
            vector = np.frombuffer(request.nparray_bytes, dtype=np.float32)

            # get the payload
            payload = vector_index.VectorPayload.from_proto(request.payload)

            # upsert the payload
            self.index.upsert(vector, payload)

            print(f"completed upsert; index has: {self.index.ngt_index.get_num_of_objects()} points")

            return vector_index_pb2.UpsertResponse(status="success")
        except Exception as e:
            print(e)
            return vector_index_pb2.UpsertResponse(status="failure")
    
    def Search(self, request, context):
        '''
        search a vector
        '''

        try: 
            print("recieved search request")
            vector = np.frombuffer(request.nparray_bytes, dtype=np.float32)
            results = self.index.search(vector)
            
            results_proto = [
                vector_index_pb2.SearchResult(
                        payload=vector_index_pb2.VectorPayload(**result.payload.__dict__),
                        score=result.score
                    )
                for result in results]
            search_response_proto = vector_index_pb2.SearchResponse(results = results_proto)
            return search_response_proto

        except Exception as e:
            print(e)
    
    def Checkpoint(self, request, context):
        # build the NGT index, and save it
        self.index.checkpoint()
        print(f"checkpoint complete")
        return vector_index_pb2.CheckpointResponse(response="checkpoint complete")
    

def serve(vector_index_path, model_name):
    print("starting gRPC service")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 10))
    vector_index_service = VectorIndexService(vector_index_path)
    print(f"opened vector index at: {vector_index_path}")
    print(f"vector index has {vector_index_service.index.ngt_index.get_num_of_objects()} points")
    vector_index_pb2_grpc.add_VectorIndexServicer_to_server(vector_index_service, server)


    port = index_network_config.port_map[model_name]
    print(f"starting service on port: {port}")

    server.add_insecure_port(f'[::]:{port}')

    try: 
        server.start()
        server.wait_for_termination()
    finally:
        # make sure to save the vectors before the program exits
        print("saving vector index...")
        vector_index_service.index.finish()
 
if __name__ == "__main__":
    '''
    
    Initialize a gRPC server for a vector index.

    the server will open the vector index specified by environment variables:


        VECTOR_INDEX_PATH : the root directory of the vector index (the directory that stores all of the other vector indices)

        MODEL_NAME : the name of the vector index to open
    
    '''

    vector_index_path = os.environ['VECTOR_INDEX_PATH']

    model_name = os.environ['MODEL_NAME']

    path = os.path.join(vector_index_path, model_name)

    # start the server
    serve(path, model_name)
