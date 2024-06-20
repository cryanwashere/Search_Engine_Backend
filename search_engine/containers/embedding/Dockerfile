FROM python:3.9-slim

WORKDIR /docker-embeddings

# Install Git
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*





# This is an installation of pytorch and corresponding torchvision

# install CPU-only pytorch
#RUN pip3 install torch==1.11.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
# install the CPU version of torchvision, (the version that is uses the previously installed version of torch as a dependency)
#RUN pip install torchvision==0.12.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu

# Here is the same thing but for another version of torch and torchvision
RUN pip install torch==2.2.0 torchvision==0.17.0 --index-url https://download.pytorch.org/whl/cpu

# several dependencies for Open Clip that can be installed manually
RUN pip install ftfy
RUN pip install protobuf
RUN pip install sentencepiece
RUN pip install tqdm
RUN pip install regex
RUN pip install huggingface_hub

# now install Open Clip without dependencies
RUN pip install --no-deps open_clip_torch



RUN pip3 install -U sentence-transformers
RUN pip3 install transformers


# special command to install gRPC
RUN python -m pip install grpcio

# This is also nescessary to use the gRPC scripts
RUN python -m pip install grpcio-tools

# install a few other things here
COPY embedding_requirements.txt . 
RUN pip install -r embedding_requirements.txt


# create a volume where the project directory is
VOLUME /project-dir

ENV VECTOR_INDEX_ROOT=/project-dir/index_v1/vector_index

# where to save the pycache (.pyc) files. Otherwise, the files will get saved in the actual project directory
ENV PYTHONPYCACHEPREFIX=/tmp

RUN apt-get update && apt-get install dnsutils -y
