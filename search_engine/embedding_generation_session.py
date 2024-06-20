import custom_logger
import page_index
import embedding_provider
import crawl_plan
import os

class EmbeddingGenerationSession:
    '''
        The purpose of this class is to manage generating embeddings for a section of content from the crawl plan.




        Paramters:
            page_index_path: the path to the root directory of the page index
            vector_index_path: the path to the root directory of the vector index
            crawl_plan_db_path: the path to the crawl plan database (SqliteDict) that contains the crawl plan
            embed_instruction: a string representing which subset of urls in the crawl plan database to generate embeddings for. This string is of the format: {crawl_start}-{crawl_end}
            model_str: a string representation for the model being used
    '''
    
    def __init__(self, page_index_path: str, vector_index_path: str, crawl_plan_db_path: str, embed_instruction: str, model_str: str):
        
        self.logger = custom_logger.Logger("EmbeddingGenerationSession")
        self.logger.verbose = True
        
        # the embedding instruction is passed to the EmbeddingGenerationSession in the same format as the crawl instruction. 
        self.start, self.end = parse_crawl_instruction(embed_instruction)
        self.embed_instruction = embed_instruction
        
        # the EmbeddingProvider object will generate the embeddings, and will access the page index through a reference
        self.embedding_provider = embedding_provider.EmbeddingProvider(model_str)
        
        # manage the page index
        self.page_index_client = page_index.PageIndexClient(page_index_path)

        # manage a connection to the crawl_plan database
        self.crawl_plan_client = crawl_plan.CrawlPlanDatabaseClient(crawl_plan_db_path)

    
    def generate(self):
        '''
            Loop through the urls, and generate embeddings for each of them        
        '''
        
        for i in range(self.start, self.end):
            url = self.crawl_plan_client.read_url(i)
            
            self.logger.log(f"[{i}] generating embeddings for url: {url[-100:]}")

            # data is obtained through a reference to the page index client
            self.embedding_provider.generate_embeddings_and_upsert(url, self.page_index_client)
        
        # now that we are done, we want to checkpoint the vector index to save our progress
        self.embedding_provider.checkpoint()

        #log_embedding_session("/project-dir/se-management/wikipedia_v1-sections.yml",self.embed_instruction)

def log_embedding_session(se_management_path, crawl_instruction):
    with open(se_management_path,'r') as f:
        se_management = yaml.safe_load(f)
        
    se_management['open_clip Embedded Sections'].append(crawl_instruction)
    print(f"{se_management}")

    with open(se_management_path,'w') as f:
        yaml.dump(se_management, f)


def parse_crawl_instruction(crawl_instruction):
    crawl_instruction = crawl_instruction.split('-')
    start, end = crawl_instruction[0], crawl_instruction[1]
    start, end = int(start), int(end)
    return start, end

if __name__ == "__main__":
    '''
        
        Embedding generation sessions will be created inside of containers, and is parameterized by environment variables which are passed to the container. The embedding session will read urls from the crawl plan, then use them to access their page data in the page index. The page data will then be loaded, and have embedding generated for it.
        
        CRAWL_PLAN_DB_PATH: the path to the database for the crawl plan

        EMBED_INSTRUCTION: a string of the format: "(embed start)-(embed end)" 

        PAGE_INDEX_PATH: the path to the page index where the crawled data is stored   

        VECTOR_INDEX_PATH: the path to the vector index of the project 
        
        MODEL_STR: a string representing the embedding model to be used

    '''
    # the path to the crawl plan database
    crawl_plan_db_path = os.environ['CRAWL_PLAN_DB_PATH']

    # a string representing what keys to crawl in the crawl session
    embed_instruction = os.environ['EMBED_INSTRUCTION']

    # path to the page index
    page_index_path = os.environ['PAGE_INDEX_PATH']

    # path to the vector index
    vector_index_path = os.environ['VECTOR_INDEX_PATH']

    model_str = os.environ['MODEL_STR']

    print(f"INITIALIZING EMBEDDING GENERATION SESSION:\n CRAWL_PLAN_DB_PATH: {crawl_plan_db_path}\n EMBED_INSTRUCTION: {embed_instruction}\n PAGE_INDEX_PATH: {page_index_path}\n VECTOR_INDEX_PATH: {vector_index_path}\n MODEL_STR: {model_str}")

    embedding_generation_session = EmbeddingGenerationSession(page_index_path=page_index_path, vector_index_path=vector_index_path, crawl_plan_db_path=crawl_plan_db_path, embed_instruction=embed_instruction, model_str=model_str)

    embedding_generation_session.generate()


 



