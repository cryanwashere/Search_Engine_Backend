import docker


# connnect to docker
docker_client = docker.from_env()

for container in docker_client.containers.list(): 
    container_id = container.id
    container_name = container.name

    if not "crawler" in container_name : continue
    container_crawl_start, container_crawl_end = int(container_name.split("_")[-2]), int(container_name.split("_")[-1])
    
    container_logs = str(container.logs())
    lines = container_logs.split("\\n")
    lines = list(filter(lambda x: "Crawling url" in x, lines))
    most_recent_url = int(lines[-1].split(" ")[-1])
    
    print(f"{container_name}: {most_recent_url} {100 * ((most_recent_url - container_crawl_start) / (container_crawl_end - container_crawl_start))}%")
    




