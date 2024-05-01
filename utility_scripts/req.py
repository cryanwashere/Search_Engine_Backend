import requests

# Define the URL of the web server
url = "http://127.0.0.1:3000/random_crawl"

# Prepare your JSON data as a dictionary
data = {
    "seed_url" : "",
}



# Send the POST request with requests
response = requests.post(url, json=data)

print(response.text)