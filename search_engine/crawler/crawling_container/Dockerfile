
FROM python:3.9-slim

WORKDIR /crawl-app

# install the required pip packages for the crawler
COPY ./crawling_server/crawling_app_requirements.txt ./
RUN pip install -r crawling_app_requirements.txt

# copy the python scripts nescessary for the crawler to work
COPY ./crawler/parse.py ./crawler/
COPY ./crawling_server/crawling_app.py ./
COPY ./wikipedia_crawl.py .
COPY ./mapped_site_crawl.py . 
COPY ./random_site_crawl.py . 

# create a volume where the crawling data gets stored
VOLUME /docker-volume


# begin the crawling process
CMD ["python", "crawling_app.py"]