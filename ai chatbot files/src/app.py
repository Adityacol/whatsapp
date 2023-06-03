from flask import Flask, request, jsonify
from helper.openai_api import chat_completion
from helper.twilio_api import send_message
from langdetect import detect
from flask_caching import Cache
import random
import spacy
from helper.sentiment_analysis import analyze_sentiment
from helper.news_api import get_latest_news

app = Flask(__name__)

# Store conversation state per user
conversations = {}

# Initialize caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Load the spaCy language model
nlp = spacy.load('en_core_web_sm')

# List of mood-based response templates
mood_responses = {
    'happy': {
        'template': "I'm glad to hear that you're feeling happy!",
        'followup': [
            "Keep spreading the positivity! 😄",
            "What's making you feel happy today?",
            "Happiness is contagious. Have a fantastic day! 🌞"
        ]
    },
    'sad': {
        'template': "I'm sorry to hear that you're feeling sad. Is there anything I can do to help?",
        'followup': [
            "Remember, you're not alone. I'm here to listen.",
            "Take some time for self-care and do something that brings you joy.",
            "Sending you virtual hugs. Stay strong! 🤗"
        ]
    },
    'angry': {
        'template': "I understand that you're feeling angry. Take a deep breath and let's work through it together.",
        'followup': [
            "Anger is a natural emotion. Let's find a constructive way to channel it.",
            "It's okay to be angry. Let's talk it out and find a solution.",
            "Take a moment to pause and reflect. We'll address the anger together. 😊"
        ]
    },
    'confused': {
        'template': "I can sense your confusion. Don't worry, I'm here to provide clarity and answers.",
        'followup': [
            "Confusion is an opportunity for growth. Let's explore and find answers together.",
            "What specifically are you confused about? Let's break it down step by step.",
            "Curiosity and confusion often go hand in hand. Embrace the journey of discovery! 🚀"
        ]
    },
    'neutral': {
        'template': "It seems like you're in a neutral mood. How can I assist you today?",
        'followup': [
            "Feel free to ask me anything you'd like to know.",
            "I'm here to help. What can I do for you?",
            "Let's make the most of this conversation. How can I make your day better? 😊"
        ]
    },
    'excited': {
        'template': "Wow! Your excitement is contagious. What's got you so thrilled?",
        'followup': [
            "Your enthusiasm is inspiring. Share your excitement with me!",
            "I love seeing your excitement. What's the best part about it?",
            "Embrace the thrill and enjoy the ride! 🎉"
        ]
    },
    'grateful': {
        'template': "Expressing gratitude is a beautiful thing. I'm grateful to have this conversation with you.",
        'followup': [
            "Gratitude uplifts the spirit. What are you grateful for today?",
            "Gratefulness brings joy. Share something you're thankful for!",
            "Your positive outlook is admirable. Keep the gratitude flowing! 🙏"
        ]
    },
    'frustrated': {
        'template': "I can sense your frustration. Let's work together to find a solution.",
        'followup': [
            "Frustration can be an opportunity for growth. How can I assist you in overcoming your frustrations?",
            "Let's break down the source of your frustration and brainstorm potential solutions.",
            "Remember, challenges are stepping stones to success! 💪"
        ]
    },
    'curious': {
        'template': "Your curiosity is admirable. Feel free to ask me anything you'd like to know.",
        'followup': [
            "Curiosity is the key to learning. What knowledge are you seeking today?",
            "I'm here to satisfy your curiosity. Ask me any question!",
            "Keep the curiosity alive. The pursuit of knowledge knows no bounds! 🧠"
        ]
    },
    'tired': {
        'template': "I understand that you're feeling tired. Take a break and recharge. I'll be here when you're ready.",
        'followup': [
            "Self-care is important. Take some time to relax and rejuvenate.",
            "Rest is crucial for well-being. Make sure to take care of yourself.",
            "Remember, a refreshed mind and body perform at their best! 💤"
        ]
    }
}


@app.route('/')
def home():
    return jsonify({
        'status': 'OK',
        'webhook_url': 'BASEURL/twilio/receiveMessage',
        'message': 'The webhook is ready.',
        'video_url': 'https://youtu.be/y9NRLnPXsb0'
    })


@app.route('/twilio/receiveMessage', methods=['POST'])
def receive_message():
    try:
        # Extract incoming parameters from Twilio
        message = request.form['Body']
        sender_id = request.form['From']

        # Retrieve or create conversation state for the user
        if sender_id not in conversations:
            conversations[sender_id] = {
                'user_id': random.randint(1, 1000000),
                'context': [],
                'sarcasm_mode': False,
                'language': '',
                'mood': 'neutral'
            }
        conversation = conversations[sender_id]

        # Detect message language
        language = detect(message)

        # Set conversation language if not set already
        if not conversation['language']:
            conversation['language'] = language

        # Add user turn to conversation context
        conversation['context'].append({
            'role': 'user',
            'message': message
        })

        # Detect user mood
        mood = detect_mood(message)

        # Update conversation mood
        conversation['mood'] = mood

        # Perform sentiment analysis on the user message
        sentiment = analyze_sentiment(message)

        # Generate response
        response = generate_response(conversation, sentiment)

        # Add bot turn to conversation context
        conversation['context'].append({
            'role': 'bot',
            'message': response
        })

        # Send the response back to Twilio
        send_message(sender_id, response)

        # Learn from user interaction
        learn_from_interaction(conversation)
    except Exception as e:
        print(f"Error: {e}")
    return 'OK', 200


def detect_mood(message: str) -> str:
    # Convert the message to lowercase for case-insensitive matching
    message = message.lower()

    # Define keyword lists for different moods
    happy_keywords = ['happy', 'joyful', 'excited', 'delighted']
    sad_keywords = ['sad', 'depressed', 'unhappy', 'heartbroken']
    angry_keywords = ['angry', 'frustrated', 'mad', 'irritated']
    confused_keywords = ['confused', 'baffled', 'perplexed', 'uncertain']
    excited_keywords = ['excited', 'thrilled', 'enthusiastic', 'eager']
    grateful_keywords = ['grateful', 'thankful', 'appreciative', 'blessed']
    curious_keywords = ['curious', 'inquisitive', 'interested', 'intrigued']
    tired_keywords = ['tired', 'exhausted', 'weary', 'fatigued']

    # Check for mood keywords in the message
    if any(keyword in message for keyword in happy_keywords):
        return 'happy'
    elif any(keyword in message for keyword in sad_keywords):
        return 'sad'
    elif any(keyword in message for keyword in angry_keywords):
        return 'angry'
    elif any(keyword in message for keyword in confused_keywords):
        return 'confused'
    elif any(keyword in message for keyword in excited_keywords):
        return 'excited'
    elif any(keyword in message for keyword in grateful_keywords):
        return 'grateful'
    elif any(keyword in message for keyword in curious_keywords):
        return 'curious'
    elif any(keyword in message for keyword in tired_keywords):
        return 'tired'
    else:
        return 'neutral'


def generate_response(conversation, sentiment):
    # Retrieve user mood and language
    mood = conversation['mood']
    language = conversation['language']

    # Randomly select a follow-up response
    followup_response = random.choice(mood_responses[mood]['followup'])

    # Generate a response based on the user's mood
    if mood in mood_responses:
        response = mood_responses[mood]['template']
    else:
        response = mood_responses['neutral']['template']

    # Append sentiment analysis result to the response
    response += f" (Sentiment: {sentiment})"

    # Append follow-up response to the main response
    response += f"\n\n{followup_response}"

    # If the user's language is English, use OpenAI API for chat completion
    if language == 'en':
        # Get the user's message
        user_message = conversation['context'][-1]['message']

        # Get the previous bot responses
        bot_responses = [turn['message'] for turn in conversation['context'] if turn['role'] == 'bot']

        # Call OpenAI API for chat completion
        completion = chat_completion(user_message, bot_responses)

        # Get the generated completion response
        completion_response = completion['choices'][0]['message']['content']

        # Append the completion response to the main response
        response += f"\n\n{completion_response}"

    # Retrieve the last user message from the context
    user_turn = [turn for turn in conversation['context'] if turn['role'] == 'user'][-1]
    user_message = user_turn['message']

    # Perform named entity recognition on the user message
    doc = nlp(user_message)
    entities = [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]

    # Append the named entities to the main response
    response += f"\n\nNamed Entities: {entities}"

    # Get the latest news headlines
    headlines = get_latest_news()

    # Append the latest news headlines to the main response
    response += f"\n\nLatest News Headlines: {headlines}"

    return response


def learn_from_interaction(conversation):
    # Retrieve the last user message from the context
    user_turn = [turn for turn in conversation['context'] if turn['role'] == 'user'][-1]
    user_message = user_turn['message']

    # Perform named entity recognition on the user message
    doc = nlp(user_message)
    entities = [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]

    # Store the named entities in the conversation context
    conversation['named_entities'] = entities


if __name__ == '__main__':
    app.run()
