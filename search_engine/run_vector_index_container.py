
command = "sudo docker run -v ~/Search_Engine:/project-dir -e MODEL_NAME=sample --rm vector_index_container"

import docker
import port_map

docker_client = docker.from_env()

model_name = "sample"
# get the port where the server will listen
port = port_map._map[model_name]



print(f"running container for: {model_name}")
container = docker_client.containers.run(
        'vector_index_container',
        volumes = ['/home/cameron/Search_Engine:/project-dir'],
        environment = [f'MODEL_NAME={model_name}'],
        name = f"vector_index.{model_name}",
        ports = {
            "50051/tcp" : port
        },
        detach=True,
    )

print(container)