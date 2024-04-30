import os 
import pickle

class DictionarySearchClient:
    '''
    
        An object that will map strings to data payloads    
    
    '''
    def __init__(self, client_path):
        self.client_path

        if not os.path.isfile(client_path):
            print("dictionary file was not found (using empty dictionary)")
            self.hash_map = dict()
        else:
            with open(client_path, "rb") as f:
                self.hash_map = pickle.load(f)
            print(f"opened dictionary with {self.point_count()} items")

    def save(self, save_path=None):

        if save_path == None: 
            save_path = self.client_path

        # save the search client
        with open(save_path, 'wb') as f:
            pickle.dump(self.hash_map, f)
            f.close()

class PageLookupClient:
    '''
    
        Map web page urls to relevant data for the urls
    
    '''
    def __init__(self, client_path):

        self.dict = DictionarySearchClient(client_path)
    
    def lookup(self, url):
        return self.dict.hash_map[url]
    
    def upsert(self, url, 

            links,
            image_urls,
            text_sections,
               
        ):
        
        payload = {
            'links' : links,
            'image_urls' : image_urls,
            'text_sections' : text_sections
        }
        
        self.dict.hash_map[url] = payload