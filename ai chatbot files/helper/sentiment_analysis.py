# sentiment_analysis.py

from transformers import pipeline

# Load sentiment analysis model
sentiment_model = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    # Perform sentiment analysis on the given text
    results = sentiment_model(text)
    
    # Extract sentiment label and score from results
    sentiment_label = results[0]['label']
    sentiment_score = results[0]['score']
    
    return sentiment_label, sentiment_score
