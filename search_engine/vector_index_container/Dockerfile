FROM python:3.9-slim


WORKDIR /vector-index-service

COPY vector_index_service_requirements.txt . 
RUN pip install -r vector_index_service_requirements.txt

# the volume gives the container access to the project directory 
VOLUME /project-dir





# where to save the pycache (.pyc) files. Otherwise, the files will get saved in the actual project directory
ENV PYTHONPYCACHEPREFIX=/tmp

# the path to the root directory of the vector index
ENV VECTOR_INDEX_PATH=/project-dir/index_v1/vector_index