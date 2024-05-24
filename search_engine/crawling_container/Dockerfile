
FROM python:3.9-slim

WORKDIR /docker-crawl

COPY ./search_engine/crawling_container/crawling_requirements.txt . 
RUN pip install -r crawling_requirements.txt






# create a volume to give the container access to the project directory
VOLUME /project-dir

# the path to where the crawl plan is 
ENV CRAWL_PLAN_DB_PATH=/project-dir/crawl_plans/wikipedia_v1.sqlite

# path to the page index
ENV PAGE_INDEX_PATH=/project-dir/index_v1/page_index

# begin the crawling process
CMD ["python", "./search_engine/crawl_session.py"]