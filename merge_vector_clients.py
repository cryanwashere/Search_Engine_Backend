import os 
import pickle

# the index is a dictionary, and all the indexes being merged will be added to this dictionary
merged_index = dict()


# select a directory containing all the clients that are being merged
clients_path = '/home/volume/index/vector_clients/vogue'
clients = os.listdir(clients_path)
clients = list(filter(lambda x : x[-3:] == 'pkl', clients))
print(f"merging clients: {clients}")

for client_file in clients: 
    client_path = os.path.join(clients_path, client_file)
    
    # open the client using python pickle
    with open(client_path, "rb") as f:
        client_index = pickle.load(f)
    
    print(f"{client_file}: {len(client_index.keys())} points")

    # merge the index from the currently iterated client with the combined index
    merged_index.update(client_index)

    # just in case memory is a problem here
    del client_index

print(f"completed merging index. merged index contains: {len(merged_index.keys())} points")

# save the index
save_path = "/home/volume/index/vector_clients/merged_clients/vogue_1.pkl"
with open(save_path, 'wb') as f:
    pickle.dump(merged_index, f)
    f.close()

print(f"merged client saved to: {save_path}. process complete. ")