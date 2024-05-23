
FROM python:3.9-slim

WORKDIR /docker-crawl

COPY ./search_engine/crawler/crawling_container/crawling_requirements.txt . 
RUN pip install -r crawling_requirements.txt

# allow the crawling script to know that it is inside of a container 
ENV LOCATION=crawling_container



# create a volume where the crawling data gets stored
VOLUME /docker-volume

# begin the crawling process
CMD ["python", "./search_engine/crawl_session.py"]