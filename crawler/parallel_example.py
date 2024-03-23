import parse
import os
import sys
from joblib import Parallel, delayed



# where all of the data is to be stored
data_root_dir = sys.argv[1]

# make sure that the proper directories exist for saving the data
pages_dir = os.path.join(data_root_dir, "pages")
if not os.path.isdir(pages_dir):
    os.mkdir(pages_dir)
images_dir = os.path.join(data_root_dir, "images")
if not os.path.isdir(images_dir):
    os.mkdir(images_dir)

# load the list of web page urls
with open("urls.txt", "r") as f:
    urls = f.read().split("\n")

# get a list of the names of all the pages that have already 
# been loaded
loaded_page_names = os.listdir(pages_dir)
loaded_page_names = [page_name.replace(".txt","") for page_name in loaded_page_names]
loaded_page_names = [page_name for page_name in loaded_page_names if page_name != '.DS_Store']
print(loaded_page_names)
print(f"already loaded {len(loaded_page_names)} pages")



# filter the list of urls, so that it will only contain urls
# that have not yet been loaded
urls = [url for url in urls if not url.split("/")[-1] in loaded_page_names]

# count the progression of the data loading
total = len(urls)


# download the page at a given url
def download_url(i):
    message = parse.process_page(urls[i], data_root_dir)
    
    loaded = len(os.listdir(os.path.join(data_root_dir, "pages")))

    print(f"({loaded} / {total}) {message}")


# please ignore this 
#for i in range(10):
#    parse.process_page(urls[i],data_root_dir)
#rm -r /Volumes/easystore/Balene_DS_V1/images/* /Volumes/easystore/Balene_DS_V1/pages/*



if __name__ == "__main__":
    # Run the loop in parallel.
    results = Parallel(n_jobs=4)(delayed(download_url)(i) for i in range(0, len(urls)))