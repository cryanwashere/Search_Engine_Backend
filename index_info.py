'''

    Given a command line argument for a directory, this searches for any saved search clients (with python '.pkl' extension), and gives information about each of the saved clients.

'''


import sys
import os 
import pickle

index_path = sys.argv[1]

client_report = ""


for path in os.listdir(index_path):
    full_path = os.path.join(index_path, path)
    ext = path.split(".")[1]

    if ext == "pkl":
        with open(full_path, "rb") as f:
            hash_map = pickle.load(f)
        client_report += f"({path}) {len(hash_map.values())} points\n"
   
print("SEARCH CLIENTS")
print(client_report)
