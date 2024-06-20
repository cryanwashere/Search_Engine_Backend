'''

    The purpose of this script is to parse the wikipedia dump XML file, and upload the page data to the page index, if the page data is not already in the page index. 

    Much of this code was adapted from: https://jamesthorne.com/blog/processing-wikipedia-in-a-couple-of-hours/

'''

import sys
sys.path.append("../../search_engine")
import parse
import page_index


from bz2 import BZ2File
import xml.sax
import logging
import multiprocessing
from multiprocessing import Process
from threading import Thread
import time


class WikiReader(xml.sax.ContentHandler):
    def __init__(self, ns_filter, callback):
        super().__init__()

        self.depth = 0

        self.tag_stack = list()

    def startElement(self, tag_name, attributes):
        #print(f"start: {tag_name}, {len(self.read_stack)}")

        print("  "*self.depth, f"<{tag_name}>")
        self.depth += 1

        self.tag_stack.append(tag_name)
    



    def endElement(self, tag_name):
        self.depth -= 1
        print("  "* self.depth, f"</{tag_name}>")

        del self.tag_stack[-1]



    def characters(self, content):
        if self.tag_stack[-1] == "text":
            pass
            
        elif self.tag_stack[-1] == "title":
            print(content)
        elif self.tag_stack[-1] == "ns":
            print(content)
    

def url_from_title(title):
    return "https://en.wikipedia.org/wiki/" + title

def process_article():
    # extract the data from the page, and then put the extracted data into the write queue
    while not (shutdown and article_queue.empty()):
        page_title, source = article_queue.get()
        
        page_url = url_from_title(page_title)

        print(page_url)
        return

        # check if the page has already been crawled
        if index_client.check_page_url(page_url):
            return
        
        page_data = parse.extract_html(source, page_url)
        write_queue.put(page_data)
        
def write_to_index():
    # write the page data on the top of the queue to the page index database
    while not (shutdown and write_queue.empty()):
        page_data = write_queue.get()
        index_client.upsert_page_data(page_data)


def display():
    while True:
        print("Queue sizes: article_queue={0} write_queue={1}. Read: {2}".format(
            article_queue.qsize(), 
            write_queue.qsize(), 
            reader.status_count))
        time.sleep(1)



if __name__ == "__main__":
    shutdown = False
    index_client = page_index.PageIndexClient('/home/cameron/Search_Engine/index_v1/page_index2')

    manager = multiprocessing.Manager()
    write_queue = manager.Queue(maxsize=2000)
    article_queue = manager.Queue(maxsize=2000)


    wiki = BZ2File('/home/cameron/Search_Engine/wikipedia/wikidump/enwiki-20240601-pages-articles-multistream.xml.bz2')

    reader = WikiReader(lambda ns: ns==0, article_queue.put)
    
    '''
    status = Thread(target=display, args=())
    status.start()

    processes = []
    for _ in range(15):
        process = Process(target=process_article)
        process.start()
    
    write_thread = Thread(target=write_to_index)
    write_thread.start()
    '''


    xml.sax.parse(wiki, reader)
    shutdown = True
