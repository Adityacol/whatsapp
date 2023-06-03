# news_api.py

import requests

NEWS_API_KEY = '9666f308108041ccbbae68f28ea728c5'

def get_latest_news():
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        
        # Extract headline and source for each article
        headlines = [f"{article['title']} - {article['source']['name']}" for article in articles]
        
        return headlines
    else:
        return []


def set_news_api_key(api_key):
    global NEWS_API_KEY
    NEWS_API_KEY = api_key
