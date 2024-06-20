helpful commands: 

```
python mapped_site_crawl.py https://site.com/sitemap.xml site
```

```
source env/bin/activate
```






```
nohup python indexer.py > /home/logs/index_nasa.out &
```


 ```
docker build -f crawling_container/Dockerfile -t crawling_container .
 ```


 ```
 docker run -v /home/volume:/docker-volume -it crawling_container /bin/bash
 ```


output the log file for the server
```
journalctl -u balene_prod > /home/logs/server_1.out
```

```
sudo docker run -e CRAWL_INSTRUCTION=400-1000 -v /home/cameron/Search_Engine:/project-dir crawling_container
```


```
python3 -m grpc_tools.protoc -I./protos --python_out=. --pyi_out=. --grpc_python_out=. protos/vector_index.proto
```




create a vector index service for a particular model: 
```python3 vector_index.py create MODEL_NAME MODEL_DIM Cosine```

start a vector index service for a particular model:
```python3 run_vector_index_container.py MODEL_NAME```


Other cool thing:
```
 1  cd /project-dir
    2  ls
    3  cd Search_Engine_Backend
    4  ls
    5  cd search_engine
    6  ls
    7  python3 embedding_provider.py
    8  python3 embedding_provider.py
    9  python3 embedding_provider.py
   10  python3 embedding_provider.py
   11  clear
   12  python3 embedding_provider.py
   13  python3 embedding_provider.py
   14  python3 embedding_provider.py
   15  python3 embedding_provider.py
   16  python3 embedding_provider.py
   17  clear
   18  python3 embedding_provider.py
   19  clear
   20  pip install --no-deps open_clip_torch
   21  python3 -c "import open_clip"
   22  pip install torchvision+cpu
   23  pip install torchvision+cpu torchvision+cpu -f https://download.pytorch.org/whl/torch_stable.html
   24  torch
   25  pip list | grep torch
   26  pip install torchvision==0.9.0+cpu  -f https://download.pytorch.org/whl/torch_stable.html
   27  pip install torchvision==0.12.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu
   28  python3 -c "import open_clip"
   29  pip install ftfy
   30  pip install protobuf
   31  pip install sentencepiece
   32  python3 -c "import open_clip"
   33  python3 embedding_provider.py
   34  clear
   35  python3 embedding_provider.py
   36  pip install ngtpy
   37  pip install ngt
   38  python3 embedding_provider.py
   39  python3 embedding_provider.py
   40  python3 embedding_provider.py
   41  python3 embedding_provider.py
   42  python3 embedding_provider.py
   43  python3 embedding_provider.py
   44  python3 embedding_provider.py
   45  python3 embedding_provider.py
   46  python3 embedding_provider.py
   47  python3 embedding_provider.py
   48  cat ~/.bash_history
   49  ls -la ~
   50  cat ~/.cache
   51  history
```