import docker

# the total number of pages in the crawl plan that need to be crawled
total_pages = 6825283

# how many pages each container instance will crawl
pages_per_container = 10000

# all the page ranges to crawl
crawl_sessions = [

        (10000, 20000),
        (20000, 30000),
       # (30000, 40000),
       # (40000, 50000)

]





docker_client = docker.from_env()


if True:
    
    for (start, end) in crawl_sessions: 

        print(f"staring crawl session client for {start}->{end}")


        container = docker_client.containers.run(
            'crawling_container',
            volumes = ['/home/cameron/Search_Engine:/project-dir'],
            environment = [f'CRAWL_INSTRUCTION={start}-{end}'],
            name = f"crawler_{start}_{end}",
            detach=True
        )

        print(container)

        # no need to use this, just helpful to look at
        command = "sudo docker run -e CRAWL_INSTRUCTION=400-1000 -v /home/cameron/Search_Engine:/project-dir crawling_container"

if False:

    containers = docker_client.containers.list()
    for container in containers: 
        last_log = container.logs.split('\n')[-1]
        print(f"{container.name}: {last_log}")
