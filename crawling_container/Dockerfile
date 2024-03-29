
FROM python:3.9-slim

WORKDIR /crawl-pod

# install the required pip packages for the crawler
COPY ./crawling_container/crawling_requirements.txt ./
RUN pip install -r crawling_requirements.txt

# copy the HTML parsing script for the crawler
COPY ./crawler/parse.py ./crawler/


# copy the main crawling scripts
COPY ./wikipedia_crawl.py .
COPY ./mapped_site_crawl.py . 

# create a volume where the crawling data gets stored
VOLUME /docker-volume


# begin the crawling process
#CMD ["python", "wikipedia_crawl.py", "10101", "20000"]