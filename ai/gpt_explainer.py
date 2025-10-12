# ai/gpt_explainer.py

import openai

openai.api_key = "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"

def explain_event(log):
    prompt = f"Explain the following OS simulator event:\n{log}\n"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()
