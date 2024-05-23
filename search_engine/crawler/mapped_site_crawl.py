import sys
import requests
from bs4 import BeautifulSoup
import os


import crawler.parse as parse
import json

import concurrent.futures
import threading



sitemap_url = sys.argv[1]





image_set = set()
image_queue = list()
#images_html = ""

pages_crawled = 0
 
def get_absolute_urls(sitemap_url):
  """
  This function takes the URL of a sitemap and returns a list of all absolute URLs in the site.

  Args:
      sitemap_url: The URL of the sitemap file.

  Returns:
      A list of absolute URLs found in the sitemap.
  """
  urls = []
  url_dict = dict()
  try:
    response = requests.get(sitemap_url)
    soup = BeautifulSoup(response.content, 'lxml')

    # Find all 'loc' tags in the sitemap
    loc_tags = soup.find_all('loc')

    # Extract URLs from 'loc' tags and make them absolute
    for loc in loc_tags:
      url = loc.text.strip()
      # Check if URL is relative
      if not url.startswith('http'):
        # If relative, make it absolute using the sitemap URL base
        base_url = sitemap_url.rsplit('/', 1)[0]
        url = f"{base_url}/{url}"
      

      if url.split("?")[0][-3:] == 'xml':
        print(f"found sub sitemap: {url}")
        nested_urls, _ = get_absolute_urls(url)
        
        sub_title = url.split("?")[-1]
        url_dict[sub_title] = nested_urls

      else:
        urls.append(url)


  except Exception as e:
    print(f"Error processing sitemap: {e}")

  
  return urls, url_dict

def process_url(url):
  # get the html for the web page
  response = requests.get(url)
  if response.status_code == 200:
    html_content = response.text  


    # this should work generally
    image_urls, text_sections = parse.extract_general_html(html_content, url)

    # iterate through the image urls
    for image_url in image_urls:
      if not image_url in image_set:
        image_set.add(image_url)

        #images_html += f"<img src='{image_url}'>"

        image_upsert_request = {
          "image_url" : image_url,
          "page_url" : url
        }

        image_queue.append(image_upsert_request)
  else:
    print(f"failed to open: {url}")

  global pages_crawled
  pages_crawled += 1
  print(f"({pages_crawled}) page: {url}, images: {len(image_urls)}")

# get all the page urls from the sitemap
page_urls, sitemap_dict = get_absolute_urls(sitemap_url)

print(f"sitemap dictionary has: {len(sitemap_dict.keys())} sub sitemaps")
for key in sitemap_dict.keys():
  print(f"crawling sitemap: {key}")

  #print(sitemap_dict[key])

  # concurrently crawl every page in the sitemap
  # this is going to put all of the image index requests into image_queue
  with concurrent.futures.ThreadPoolExecutor(max_workers=80) as executor:
    executor.map(process_url, sitemap_dict[key])

  # save the image queue from the current sitemap
  print(f"completed crawling {key} with {len(image_queue)} image urls")
  with open(os.path.join('/home/volume/index/image_queue', sys.argv[2] + '_' + key + '.json'),'w') as f:
    json.dump(image_queue, f)
  
  # empty the image queue so that it can be used again for the next sitemap
  image_queue = list()
  pages_crawled = 0




#print(f"there are {len(page_urls)} urls (directly from the sitemap). crawling those.")
#with concurrent.futures.ThreadPoolExecutor(max_workers=80) as executor:
#  executor.map(process_url, page_urls)

#save_path = os.path.join('/home/index/image_queue/', sys.argv[2] + '.json')
#print(f"completed crawling with {len(image_queue)} image urls")
#with open(save_path,'w') as f:
#  json.dump(image_queue, f)

#with open("sample.html",'w') as f:
#  f.write(images_html)





