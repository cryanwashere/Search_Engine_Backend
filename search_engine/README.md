# containers/

A folder containing folders for each container that is used in the search engine process


# controllers/ 

Meant to be used for files that define how containers are used and started. There is nothing important in here right now

# proto/

Store files for gRPC protocols. The proto files define how each gRPC service is used.

# traditional_search/

Don't look here, there is nothing interesting


# .

There are a lot of files here. I put all the files in this folder, because it is the easiest way to avoid complicated import errors, and other difficulties. All of the containers have a the project directory attached as a volume, so they will run code from this directory. 

There is no point in explaining every file, and not every file is even used. Only the most important files will be explained: 



# crawl_plan.py

Connect to a database containing urls to crawl, and retrieve the urls (given an index)


# crawl_session.py

Perform the crawling process


# docker-compose.yml

Define container services, and the network that the containers use to communicate. Using this file, services can be started with the ```docker-compose``` command. For example:

```docker-compose up crawler```

This would start the crawler. The subset URLs that the crawler is instructed to crawl are passed to it by an environment variable, defined in the docker-compose file


# embedding_provider.py

This contains the code for generating embeddings, and upserting them to a vector index. 


# page_index.py

Store data from pages, and images from pages in a database


# vector_index_client.py 

This is how the vector index is accessed. The ```VectorIndexClient``` connects to a ```VectorIndexService``` over gRPC.