import requests

url = "https://159.89.10.125:80/crawl_wikipedia"

info = {
        "start_url" : "15001",
        "end_url" : "15100"

}

# Set the Content-Type header to application/json
headers = {"Content-Type": "application/json"}

# Send the POST request with requests
response = requests.post(url, json=info, headers=headers)

# Check the response status code
if response.status_code == 200:
  print("Data sent successfully!")
else:
  print(f"Error: {response.status_code}")
  print(response.text)  # Optional: Print the error response
