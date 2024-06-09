import docker
import sys

# the total number of pages in the crawl plan that need to be crawled
total_pages = 6825283

# how many pages each container instance will crawl
pages_per_container = 40000

# connect to docker
docker_client = docker.from_env()


def next_sections(n: int):
    '''
    what should be the start and end of the next crawl? 
    '''
    # where we are starting the crawl
    with open('/home/cameron/Search_Engine/container_management/wikipedia_v1-sections.txt','r') as f:
        crawl_sections = f.read()
        crawl_start = int(crawl_sections.split('\n')[-1])



    itr = (total_pages - crawl_start) // pages_per_container
    section_plan = [((i * pages_per_container) + crawl_start, ((i+1) * pages_per_container) + crawl_start) for i in range(itr)]
    
    return section_plan[:n]

    
crawl_sections = next_sections(8)

print(f"initializing containers for the following sections: {crawl_sections}")
proceed = input("is this ok? [y/n]")
if proceed != "y":
    exit()


for (start, end) in crawl_sections: 

    print(f"staring crawl session client for {start}->{end}")


    container = docker_client.containers.run(
        'crawling_container',
        volumes = ['/home/cameron/Search_Engine:/project-dir'],
        environment = [f'CRAWL_INSTRUCTION={start}-{end}'],
        name = f"crawler_{start}_{end}",
        detach=True
    )

    print(container)

# now we need to record what sections have been crawled

with open('/home/cameron/Search_Engine/container_management/wikipedia_v1-sections.txt','a') as f:
    for section in crawl_sections:
        f.write(str(section[-1]) + "\n")
