# ai/gpt_explainer.py

import openai

openai.api_key = "My Open_API key "

def explain_event(log):
    prompt = f"Explain the following OS simulator event:\n{log}\n"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()
