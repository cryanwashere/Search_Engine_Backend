
command = "sudo docker run -v ~/Search_Engine:/project-dir -e MODEL_NAME=sample --rm vector_index_container"

import docker
import port_map
import sys
import uuid

docker_client = docker.from_env()

model_name = sys.argv[1]
# get the port where the server will listen
port = port_map._map[model_name]


print(f"serving vector index for model: {model_name}")
print(f"vector index will be served on port: {port}")

# the name of the container needs to be unique, so this will add an id string to the name 
# note: this has no functionality, it is just for naming the container
container_name_uuid = str(uuid.uuid1())[:8]
container_name = f"vector_index.{model_name}.{container_name_uuid}"

container = docker_client.containers.run(
        'vector_index_container',
        volumes = ['/home/cameron/Search_Engine:/project-dir'],
        environment = [f'MODEL_NAME={model_name}'],
        name = container_name,
        ports = {
            "50051/tcp" : port
        },
        detach=True,
    )

print(container)