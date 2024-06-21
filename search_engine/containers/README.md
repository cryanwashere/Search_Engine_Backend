# crawling/

container that performs the crawling. 

# embedding/ 

contaner that loads data from the page index, generates embeddings, and upserts the embeddings to their respective vector indexes

# search/ 

container that runs a gRPC service for the search engine. This is helpful because it allows the app to be written in whatever programming language we want, and searches can be performed in a container


# vector_index/
container that runs a gRPC service for a vector index