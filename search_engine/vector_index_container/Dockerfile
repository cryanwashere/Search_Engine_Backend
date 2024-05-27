FROM python:3.10-slim


WORKDIR /vector-index-service

# special command to install gRPC
RUN python -m pip install grpcio

# This is also nescessary to use the gRPC scripts
RUN python -m pip install grpcio-tools

COPY vector_index_requirements.txt . 
RUN pip install -r vector_index_requirements.txt



# the volume gives the container access to the project directory 
VOLUME /project-dir

# where to save the pycache (.pyc) files. Otherwise, the files will get saved in the actual project directory
ENV PYTHONPYCACHEPREFIX=/vector-index-service

# the path to the root directory of the vector index
ENV VECTOR_INDEX_PATH=/project-dir/index_v1/vector_index


CMD ["python3","/project-dir/Search_Engine_Backend/search_engine/vector_index_service.py"] 