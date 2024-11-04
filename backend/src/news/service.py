import requests

def fetch_news_data():
    response = requests.get("https://newsapi.org/v2/everything?q=price&apiKey=your_api_key")
    return response.json()
