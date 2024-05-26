import docker


docker_client = docker.from_env()


if True:
    start = 2500
    end = 10000

    print("staring crawl session client...")


    container = docker_client.containers.run(
        'crawling_container',
        volumes = ['/home/cameron/Search_Engine:/project-dir'],
        environment = [f'CRAWL_INSTRUCTION={start}-{end}'],
        name = f"crawler_{start}_{end}",
        detach=True
        )

    # no need to use this, just helpful to look at
    command = "sudo docker run -e CRAWL_INSTRUCTION=400-1000 -v /home/cameron/Search_Engine:/project-dir crawling_container"

if False:

    containers = docker_client.containers.list()
    for container in containers: 
        last_log = container.logs.split('\n')[-1]
        print(f"{container.name}: {last_log}")