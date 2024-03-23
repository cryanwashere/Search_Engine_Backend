'''

    The purpose of this file is to recursively search through wikipedia pages, and creata a giant text file of links to wikipedia pages.

'''



import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import time
import random
import os

# the maximum number of urls that this file will gather
url_max = 100000

def pause_random_time():
    # Generate a random float between 0.1 and 1.0 (adjust the range as needed)
    random_time = random.uniform(0.1, 0.5)
    time.sleep(random_time)



def search_HTML(html_content):
    
    # initialize parser
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a')

    # get only the links with hrefs
    links = [link for link in links if "href" in link.attrs]

    # get the references from the links
    links = [link["href"] for link in links]

    # clear out empy links
    links = [link for link in links if link != '']
    
    _links = list()
    for link in links:
        
        if "wikipedia.org" in link:
            continue

        if "wikidata.org" in link:
            continue

        if "wikimedia" in link:
            continue

        if "https://" in link:
            continue

        if ":" in link:
            continue

        if "#" in link:
            continue

        if "%" in link:
            continue

        if "&" in link:
            continue
        
        if 'disambiguation' in link:
            continue

        if not "https://" in link:
            link = urljoin("https://wikipedia.org",link)

        _links.append(link)

    links = _links
    del _links

    return links
    



 



