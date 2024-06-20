import search

import grpc
import search_pb2
import search_pb2_grpc

from PIL import Image
import io

import index_network_config
from concurrent import futures


class SearchService(search_pb2_grpc.SearchServicer):
    def __init__(self):
        # initalize the search client
        self.search_client = search.SearchEngineClient(
            '/project-dir/index_v1/vector_index',
            '/project-dir/index_v1/page_index'
        )

    def SearchImage(self, request, context):
        print("recieved image search request")

        # parse the request for the image data
        image_bytes = request.image_bytes
        image = Image(io.BytesIO(image_bytes))

        # search the image
        results = self.search_client.search_image(image)

        # convert the results into the proper gRPC protocol
        results_proto = [
            search_pb2.SearchEngineResult(
                image_url = result.image_url,
                page_url = result.page_url,
                text_section_idx = -1,
                text_preview = ""
            )
            for result in results]
        return search_pb2.SearchEngineResponse(
            results = results_proto
        )

    def SearchText(self, request, context):
        print("recieved text search request")

        query = request.text
        results = self.client.search_text(query)

        # convert the results into the proper gRPC protocol
        results_proto = [
            search_pb2.SearchEngineResult(
                image_url = result.image_url,
                page_url = result.page_url,
                text_section_idx = result.text_section_idx,
                text_preview = ""
            )
            for result in results]
        return search_pb2.SearchEngineResponse(
            results = results_proto
        )

def serve():
    print("starting gRPC search engine service")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    search_service = SearchService()
    print("completed initializing search service")

    search_pb2_grpc.add_SearchServicer_to_server(search_service, server)

    port = index_network_config.search_engine_port
    print(f"starting search service on port: {port}")

    server.add_insecure_port(f'[::]:{port}')

    
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()