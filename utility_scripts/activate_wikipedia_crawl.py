import os

for i in range(20):
    os.system("/home/env/bin/python /home/sshfs_volume/Search_Engine_Backend/search_engine/crawler/wikipedia_title_crawl.py")
    print("finished crawl...")
