'''
This creates a gRPC server that hosts the naturify classification model
'''

import grpc 
import classification_pb2
import classification_pb2_grpc
import index_network_config

from PIL import Image
import io
import naturify

class NaturifyClassificationService(classification_pb2_grpc.ClassificationServicer):
    def __init__(self):
        self.inferencer = naturify.NaturifyModelInferencer()

    def ClassifyImage(self, request, context):
        image_bytes = request.image_bytes

        # parse the bytes for the image into a Pillow Image
        image = Image(io.BytesIO(image_bytes))

        classification_results = self.inferencer.inference(image)

        return classification_pb2.ClassificationResponse(results=[
            classification_pb2.ClassificationResult(
                class_name=result['species']['name'],
                class_id=result['species']['id'],
                class_metadata=str(result['species']),
                confidence=result['score']
            )
        for result in classification_results])
