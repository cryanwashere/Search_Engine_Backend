import ngtpy
import random

index = ngtpy.Index(b'/home/cameron/Search_Engine/index_v1/vector_index/ngt_sample')

dim = 128

vectors = [[random.random() for _ in range(dim)] for _ in range(100)]


#index.batch_insert(vectors)
#index.save()


results = index.search(vectors[0], 3)
for i, (id, distance) in enumerate(results) :
    print(str(i) + ": " + str(id) + ", " + str(distance))