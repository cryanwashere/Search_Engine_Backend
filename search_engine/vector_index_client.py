import grpc
import vector_index_pb2
import vector_index_pb2_grpc
import numpy as np
import vector_index

class VectorIndexClient:
    '''

        This class manages a connection to a vector index over gRPC
    
    '''

    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = vector_index_pb2_grpc.VectorIndexStub(channel)
    
    def upsert(self, vector: np.array, payload: vector_index.VectorPayload):
        '''
        Upserts the point to the vector index, with its corresponding payload
        '''
        
        payload_proto = vector_index_pb2.VectorPayload(**payload)

        upsert_request_proto = vector_index_pb2.UpsertRequest(
            payload = payload_proto,
            nparray_bytes = vector.tobytes()
        )

        upsert_response = self.stub.Upsert(upsert_request_proto)

        return upsert_response.status