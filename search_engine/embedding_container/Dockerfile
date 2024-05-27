FROM python:3.9-slim

WORKDIR /docker-embeddings

# install CPU-only pytorch
RUN pip3 install torch==1.11.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
#RUN pip3 install open_clip_torch
RUN pip3 install -U sentence-transformers


# special command to install gRPC
RUN python -m pip install grpcio

COPY embedding_generation_requirements.txt . 
RUN pip install -r embedding_generation_requirements.txt


# create a volume where the project directory is
VOLUME /project-dir

ENV VECTOR_INDEX_ROOT=/project-dir/index_v1/vector_index

# where to save the pycache (.pyc) files. Otherwise, the files will get saved in the actual project directory
ENV PYTHONPYCACHEPREFIX=/tmp