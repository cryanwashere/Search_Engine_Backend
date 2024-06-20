# app/

Source code for a backend, written in Golang. This is far from complete. Eventually the backend is intended to create a gRPC connection to the ```search``` container, which is how it will be used to get search results

# processors/ 

Folders for code that is used to manually gather content, as an alternative to crawling, when such an option is available.

# search_engine/ 

Everything used for crawling, storing, and searching content. Most important things are in this folder.


# static/ 

Things that are meant to be served statically by the app

# app.py

The FastAPI (python) server for the search. This is intended to be used just for testing the search

# search_page.html

Page without any web UI for testing