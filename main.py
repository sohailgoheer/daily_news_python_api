import requests

# Your API key
api_key = "5410c045f0e2413cb72615e950a6cd1e"
# https://newsapi.org/

# URL with query parameters and API key
url = (
    "https://newsapi.org/v2/everything?q=tesla&"
    "from=2024-09-08&"
    "sortBy=publishedAt&"
    f"apiKey={api_key}"
)
# Make the GET request
response = requests.get(url)


# Get the response data as a dictionary
content = response.json()

# Access and print article titles and descriptions
for article in content["articles"]:
    print(f"Title: {article['title']}")
    print(f"Description: {article['description']}")
    print()  # Print a blank line for better readability between articles