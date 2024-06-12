'''

Each of the vector index services need to be run on their own port. This is the simplest way to map the names of models, to the ports where their vector index gRPC servers are listening.

This file can simply be imported, and used to get correct ports

'''
_map = {
    "sample" : 50000,
    "open_clip_image" : 50001,
    "open_clip_text" : 50002,
}