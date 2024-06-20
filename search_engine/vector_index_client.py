import grpc
import vector_index_pb2
import vector_index_pb2_grpc
import numpy as np
import vector_index
from typing import List
import custom_logger
import index_network_config


class VectorIndexClient:
    '''

        This class manages a connection to a vector index over gRPC
    
    '''

    def __init__(self, model_name, hostname=None):
        self.logger = custom_logger.Logger(f"VectorIndexClient[{model_name}]")
        self.logger.verbose = True


        port = index_network_config.port_map[model_name]
        
        # on the index network, the domain name for vector index server is the model whose embeddings it serves
        service_route = f'{model_name}_service:{port}' if hostname is None else f'{hostname}:{port}'
        self.logger.log(f"initializing client for service: {service_route}")

        self.channel = grpc.insecure_channel(service_route)
        self.stub = vector_index_pb2_grpc.VectorIndexStub(self.channel)
    
    def upsert(self, vector: np.array, payload: vector_index.VectorPayload):
        '''
        Upserts the point to the vector index, with its corresponding payload
        '''
       
        payload_proto = vector_index_pb2.VectorPayload(**payload.__dict__)

        upsert_request_proto = vector_index_pb2.UpsertRequest(
            payload = payload_proto,
            nparray_bytes = vector.tobytes()
        )

        upsert_response = self.stub.Upsert(upsert_request_proto)

        return upsert_response.status
    
    def search(self, vector: np.array) -> List[vector_index.SearchResult]:
        search_request_proto = vector_index_pb2.SearchRequest(nparray_bytes=vector.tobytes())

        search_response = self.stub.Search(search_request_proto)
        
        results = list()
        for result_proto in search_response.results:
            payload = vector_index.VectorPayload(
                text_section_idx=result_proto.payload.text_section_idx,
                image_url=result_proto.payload.image_url,
                page_url=result_proto.payload.page_url
            )
            score = result_proto.score
            results.append(vector_index.SearchResult(
                payload=payload,
                score=score
            ))
        return results
            
    
    def checkpoint(self):
        checkpoint_request_proto = vector_index_pb2.CheckpointRequest(request="")
        checkpoint_response = self.stub.Checkpoint(checkpoint_request_proto)
        print(f"checkpoint status: {checkpoint_response}")

 
if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        prog='VectorIndexClient',
        description='perform various functions with a vector index client'
    )
    parser.add_argument(
        'command',
        choices=['sample_test', 'search']
    )
    args = parser.parse_args()
    
    if args.command == "sample_test":
        client = VectorIndexClient("sample")

        sample_vector = np.random.randn(128).astype(np.float32)

        sample_payload = vector_index.VectorPayload(
            text_section_idx=-1,
            image_url="image",
            page_url="some page"
        )
        client.upsert(sample_vector, sample_payload)

        client.checkpoint()

    elif args.command == "search":
        client = VectorIndexClient('open_clip_image', hostname='localhost')
        
        from PIL import Image 
        image = Image.open('/home/cameron/Search_Engine/flower.jpg')

        import embedding_provider
        provider = embedding_provider.EmbeddingProvider("open_clip")

        image_embedding = provider.open_clip_embed_image(image).astype(np.float32)


        search_results = client.search(image_embedding)
        #result_html = ""
        #for result in search_results:
        #    result_html += f'<img src="{result.payload.image_url}"><p>{result.score}</p><a href="{result.#payload.page_url}">page</a><br>'
        #with open("/home/cameron/Search_Engine/test_result.html",'w') as f:
        #    f.write(result_html)


