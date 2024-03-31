import requests

# Define the URL of the web server
url = "http://127.0.0.1:3000/crawl_wikipedia"

# Prepare your JSON data as a dictionary
data = {
  "crawl_start" : 15100,
  "crawl_end" : 20000
}



# Send the POST request with requests
response = requests.post(url, json=data)

print(response.text)