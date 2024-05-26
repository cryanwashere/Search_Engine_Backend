import grpc_compiled.vector_index_pb2
import grpc_compiled.vector_index_pb2_grpc
import numpy as np
import vector_index
from concurrent import futures

class VectorIndexService(vector_index_pb2_grpc.VectorIndexServicer):
    '''
    
        create a gRPC service that allows a vector index to be accessed over a network
    
    '''


    def Upsert(self, request, context):
        print(f"recieved upsert request")
        
        
        # the vector to upsert
        vector = np.frombuffer(request.nparray_bytes, dtype=np.float32)

        payload = vector_index.VectorPayload(
                    request.
                )

def serve():
    server = grpc.server(futures = concurrent.futures.ThreadPoolExecutor(max_workers = 10))
    vector_index_pb2_grpc.add_VectorIndexServicer_to_server(VectorIndexService(),server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
