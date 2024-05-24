'''

    The purpose of this file is to contain functions that will be used to parse the HTML content of web pages


'''

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import re
import time

import os
from io import BytesIO
#from PIL import Image
import sys
from dataclasses import dataclass



def extract_wiki_links(html_content):
    
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


def remove_wiki_references(text) -> str:
    '''
    remove references from the wikipedia text
    '''

    # Define a regular expression pattern to match substrings of the form '[x]'
    pattern = r'\[\d+\]'

    # Use re.sub to replace all occurrences of the pattern with an empty string
    result_string = re.sub(pattern, '', text)
    return result_string

def filter_image_tag(tag) -> bool:
    '''
        returns a boolean that determines whether or not an image should be included in the index, given its HTML tag
    '''

    # get rid of images that are really small. It is unlikely that they will contain any desirable content
    try:
        if 'width' in tag.attrs:
            if int(tag['width']) < 50:
                return False
        if 'height' in tag.attrs:
            if int(tag['height']) < 50:
                return False
    except Exception as e: 
        #print(f"Error filtering image tag: {e}")
        return False
    
    # here are some words that generally indicate that an image is undesirable
    image_url = tag['src']

    if 'static' in image_url:
        return False
    if 'wikipedia' in image_url and 'logo' in image_url:
        return False
    # wikipedia pages have a lot of pictures of equations, which do not really help the index at all
    if 'math/render/svg' in image_url:
        return False


    if 'data:' in image_url:
        return False
    if 'gif' in image_url:
        return False
    if 'svg' in image_url:
        return False
    
    #if "static/images/icons/wikipedia.png" in image_url:
    #    return False
        
    return True

def filter_text_tag(tag) -> bool:

    '''
        determines whether html tags for text sections are desirable for the index
    '''

    # get the text from the html tag
    text = tag.get_text()

    if len(text) < 50:
        return False
    if '\displaystyle' in text:
        return False

    return True
                
                
def extract_html(html_content, url) -> dict[str, object]:
    '''
    
        Takes in the HTML for a web page, and the web page's URL. It will then return a python dictionary containing all of the important data from the web page, to be stored in the page index. 
    
    '''

    # the list of image urls that the function will return 
    image_urls = list()

    # the list of text segments desirable for the index that the function will return 
    text_sections = list()

    # parse HTML with beautifulsoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # iterate through every image on the web page
    for img_tag in soup.find_all('img'):
        if 'src' in img_tag.attrs:

            # use the filter_tag function to determine whether or no the image should part of the index
            if not filter_image_tag(img_tag):
                # this will print the url in red
                #print(f"\033[41m {img_tag['src']} \033[0m")
                continue
            else:
                # this will print the url normally
                #print(img_tag['src'])
                pass
            
            # get the url form the image's tag
            image_url = img_tag['src']

            # if the image_url is a relative url, make it an absolute url 
            if not 'https://' in image_url:
                image_url = urljoin(url, image_url)
        
            
            image_urls.append(image_url)
    
    # iterate through every section of text on the web page
    for text_tag in soup.find_all('p'):

        if not filter_text_tag(text_tag):
            continue
        text = text_tag.get_text()
        text = remove_wiki_references(text)
        #print(text)
        text_sections.append(text)

    # determine if the page is a redirect
    canonical = soup.find('link', {'rel': 'canonical'})
    redirect = canonical['href'] != url

    return ParseResult(
        page_dict = {
        "page_url" : url,
        "text_sections" : text_sections,
        "image_urls" : image_urls,
        "time_indexed" : str(time.time())
        },
        redirected = redirect
    )



@dataclass
class ParseResult:
    page_dict: dict
    redirected: bool