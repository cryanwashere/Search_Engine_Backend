import grpc 
import embedding_pb2
import embedding_pb2_grpc
import io
from PIL import Image
import embedding_provider

class EmbeddingService(embedding_pb2_grpc.EmbeddingServiceServicer):
    '''
        Create a gRPC service that will allow models to be inferenced over a network

        Parameters: 
            model_name: the name of the model that the service is inferencing
    '''

    def __init__(self, model_name):
        self.model_namge = model_name

        self.logger = custom_logger.Logger(f"EmbeddingService")

        self.logger.log(f"Creating embedding service for {model_name}")
        self.logger.verbose = True

        # initialize the model
        self.provider = embedding_provider.EmbeddingProvider(model_name)

    def EmbedImage(self, request, context):
        # convert the raw bytes to an image
        image = Image(io.BytesIO(request.image_bytes))

        # generate an embedding for the image
        embedding = self.provider.embed_image(image)

        # convert the embedding into a list
        embedding = list(embedding)

        response = embedding_pb2.Embedding(
            values=embedding,
            dim=len(embedding)
        )


    def EmbedText(self, request, context):
        pass


def serve(model_name):
    print("starting gRPC service")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 10))
    embedding_service = EmbeddingService(model_name)
   
    embedding_pb2_grpc.add_EmbeddingServiceServicer_to_server(embedding_service, server)


    port = index_network_config.embedding_port_map[model_name]
    print(f"starting service on port: {port}")

    server.add_insecure_port(f'[::]:{port}')

    try: 
        server.start()
        server.wait_for_termination()

 
if __name__ == "__main__":
    '''
    
    Initialize a gRPC server for an embedding model.

    the server will open the vector index specified by environment variables:

        MODEL_NAME : the name of the vector index to open
    
    '''

    model_name = os.environ['MODEL_NAME']


    # start the server
    serve(model_name)
