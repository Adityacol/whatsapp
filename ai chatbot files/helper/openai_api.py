import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')


def chat_completion(prompt: str, user_id: str, tokens: int = 50, language: str = 'en') -> str:
    if language == 'hi':
        model = 'text-davinci-hi-003'
    else:
        model = 'text-davinci-003'

    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=tokens,
        temperature=0.7,
        n=1,
        stop=None,
        user=user_id
    )

    return response.choices[0].text.strip()
